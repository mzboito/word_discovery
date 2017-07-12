# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Sequence-to-sequence model with an attention mechanism."""

import numpy as np
import tensorflow as tf
import re

from translate import utils
from translate import decoders
from collections import namedtuple


class Seq2SeqModel(object):
    """Sequence-to-sequence model with attention.

    This class implements a multi-layer recurrent neural network as encoder,
    and an attention-based decoder. This is the same as the model described in
    this paper: http://arxiv.org/abs/1412.7449 - please look there for details,
    or into the seq2seq library for complete model implementation.
    This class also allows to use GRU cells in addition to LSTM cells, and
    sampled softmax to handle large output vocabulary size. A single-layer
    version of this model, but with bi-directional encoder, was presented in
      http://arxiv.org/abs/1409.0473
    and sampled softmax is described in Section 3 of the following paper.
      http://arxiv.org/abs/1412.2007
    """

    def __init__(self, encoders, decoder, learning_rate, global_step, max_gradient_norm, dropout_rate=0.0,
                 freeze_variables=None, lm_weight=None, max_output_len=50, attention=True, feed_previous=0.0,
                 optimizer='sgd', max_input_len=None, decode_only=False, len_normalization=1.0,
                 reinforce_baseline=True, softmax_temperature=10.0, loss_function='xent', rollouts=None,
                 partial_rewards=False, **kwargs):
        self.lm_weight = lm_weight
        self.encoders = encoders
        self.decoder = decoder

        self.learning_rate = learning_rate
        self.global_step = global_step

        self.encoder_count = len(encoders)
        self.trg_vocab_size = decoder.vocab_size
        self.trg_cell_size = decoder.cell_size
        self.binary_input = [encoder.name for encoder in encoders if encoder.binary]

        self.max_output_len = max_output_len
        self.max_input_len = max_input_len
        self.len_normalization = len_normalization

        if dropout_rate > 0:
            self.dropout = tf.Variable(1 - dropout_rate, trainable=False, name='dropout_keep_prob')
            self.dropout_off = self.dropout.assign(1.0)
            self.dropout_on = self.dropout.assign(1 - dropout_rate)
        else:
            self.dropout = None

        self.feed_previous = tf.constant(feed_previous, dtype=tf.float32)
        self.feed_argmax = tf.constant(True, dtype=tf.bool)  # feed with argmax or sample

        self.encoder_inputs = []
        self.encoder_input_length = []

        self.extensions = [encoder.name for encoder in encoders] + [decoder.name]
        self.encoder_names = [encoder.name for encoder in encoders]
        self.decoder_name = decoder.name
        self.extensions = self.encoder_names + [self.decoder_name]
        self.freeze_variables = freeze_variables or []
        self.max_gradient_norm = max_gradient_norm

        for encoder in self.encoders:
            if encoder.binary:
                placeholder = tf.placeholder(tf.float32, shape=[None, None, encoder.embedding_size],
                                             name='encoder_{}'.format(encoder.name))
            else:
                # batch_size x time
                placeholder = tf.placeholder(tf.int32, shape=[None, None],
                                             name='encoder_{}'.format(encoder.name))

            self.encoder_inputs.append(placeholder)
            self.encoder_input_length.append(
                tf.placeholder(tf.int64, shape=[None], name='encoder_{}_length'.format(encoder.name))
            )


        # starts with BOS, and ends with EOS  (time x batch_size)
        self.targets = tf.placeholder(tf.int32, shape=[None, None], name='target_{}'.format(self.decoder.name))
        self.target_weights = decoders.get_weights(self.targets[1:,:], utils.EOS_ID, time_major=True,
                                                   include_first_eos=True)
        self.target_length = tf.reduce_sum(self.target_weights, axis=0)

        if loss_function == 'xent' or decode_only:  # FIXME: use tensor instead
            self.rollouts = None
        else:
            self.rollouts = rollouts

        self.partial_rewards = partial_rewards

        parameters = dict(encoders=encoders, decoder=decoder, dropout=self.dropout,
                          encoder_input_length=self.encoder_input_length, rollouts=self.rollouts)

        self.attention_states, self.encoder_state = decoders.multi_encoder(self.encoder_inputs, **parameters)
        decoder = decoders.attention_decoder if attention else decoders.decoder

        (self.outputs, self.attention_weights, self.decoder_outputs, self.beam_tensors,
         self.sampled_output, self.rewards) = decoder(
            attention_states=self.attention_states, initial_state=self.encoder_state,
            targets=self.targets, feed_previous=self.feed_previous,
            decoder_input_length=self.target_length, feed_argmax=self.feed_argmax, **parameters
        )

        self.beam_output = decoders.softmax(self.outputs[0, :, :], temperature=softmax_temperature)

        optimizers = self.get_optimizers(optimizer, learning_rate)

        self.xent_loss, self.reinforce_loss, self.baseline_loss = None, None, None
        self.update_op, self.sgd_update_op, self.baseline_update_op = None, None, None
        self.reward = None    # sentence-level reward

        if loss_function == 'xent':
            self.init_xent(optimizers, decode_only)
        else:
            self.init_reinforce(optimizers, reinforce_baseline, decode_only)
            self.init_xent(optimizers, decode_only=True)   # used for eval

    @staticmethod
    def get_optimizers(optimizer_name, learning_rate):
        sgd_opt = tf.train.GradientDescentOptimizer(learning_rate=learning_rate)
        if optimizer_name.lower() == 'adadelta':
            # same epsilon and rho as Bahdanau et al. 2015
            opt = tf.train.AdadeltaOptimizer(learning_rate=1.0, epsilon=1e-06, rho=0.95)
        elif optimizer_name.lower() == 'adam':
            opt = tf.train.AdamOptimizer(learning_rate=0.001)
        else:
            opt = sgd_opt

        return opt, sgd_opt

    def get_update_op(self, loss, opts, global_step=None):
        # compute gradient only for variables that are not frozen
        frozen_parameters = [var.name for var in tf.trainable_variables()
                             if any(re.match(var_, var.name) for var_ in self.freeze_variables)]
        params = [var for var in tf.trainable_variables() if var.name not in frozen_parameters]

        gradients = tf.gradients(loss, params)
        clipped_gradients, _ = tf.clip_by_global_norm(gradients, self.max_gradient_norm)

        update_ops = []
        for opt in opts:
            update_op = opt.apply_gradients(zip(clipped_gradients, params), global_step=global_step)
            update_ops.append(update_op)

        return update_ops

    def init_xent(self, optimizers, decode_only=False):
        self.xent_loss = decoders.sequence_loss(logits=self.outputs, targets=self.targets[1:, :],
                                                weights=self.target_weights)

        if not decode_only:
            self.update_op, self.sgd_update_op = self.get_update_op(self.xent_loss, optimizers, self.global_step)

    def init_reinforce(self, optimizers, reinforce_baseline=True, decode_only=False):
        if self.rollouts is None or self.rollouts <= 1:
            hyps = tf.transpose(self.sampled_output)
            refs = tf.transpose(self.targets[1:,:])

            with tf.device('/cpu:0'):
                self.reward = decoders.batch_bleu(hyps, refs, eos_id=utils.EOS_ID)
                self.rewards = decoders.batch_partial_bleu(hyps, refs, eos_id=utils.EOS_ID)
                self.rewards = tf.transpose(self.rewards)

            if not self.partial_rewards:
                time_steps = tf.shape(self.decoder_outputs)[0]
                batch_size = tf.shape(self.decoder_outputs)[1]

                self.rewards = tf.reshape(tf.tile(self.reward, [time_steps]),
                                          shape=tf.pack([time_steps, batch_size]))

        if reinforce_baseline:
            reward = decoders.reinforce_baseline(self.decoder_outputs, self.rewards)
            weights = decoders.get_weights(self.sampled_output, utils.EOS_ID, time_major=True,
                                           include_first_eos=False)
            self.baseline_loss = decoders.baseline_loss(reward=reward, weights=weights)
        else:
            reward = self.rewards
            self.baseline_loss = tf.constant(0.0)

        weights = decoders.get_weights(self.sampled_output, utils.EOS_ID, time_major=True,
                                       include_first_eos=True)   # FIXME: True or False?
        self.reinforce_loss = decoders.sequence_loss(logits=self.outputs, targets=self.sampled_output,
                                                     weights=weights, reward=reward)

        if not decode_only:
            self.update_op, self.sgd_update_op = self.get_update_op(self.reinforce_loss,
                                                                    optimizers,
                                                                    self.global_step)

            if reinforce_baseline:
                baseline_opt = tf.train.AdamOptimizer(learning_rate=0.001)
                self.baseline_update_op, = self.get_update_op(self.baseline_loss, [baseline_opt])
            else:
                self.baseline_update_op = tf.constant(0.0)   # dummy tensor

    def step(self, session, data, update_model=True, align=False, use_sgd=False, **kwargs):
        if self.dropout is not None:
            session.run(self.dropout_on)

        batch = self.get_batch(data)
        encoder_inputs, targets, encoder_input_length = batch

        input_feed = {self.targets: targets}

        for i in range(self.encoder_count):
            input_feed[self.encoder_input_length[i]] = encoder_input_length[i]
            input_feed[self.encoder_inputs[i]] = encoder_inputs[i]

        output_feed = {'loss': self.xent_loss}
        if update_model:
            output_feed['updates'] = self.sgd_update_op if use_sgd else self.update_op
        if align:
            output_feed['attn_weights'] = self.attention_weights

        res = session.run(output_feed, input_feed)

        return namedtuple('output', 'loss attn_weights')(res['loss'], res.get('attn_weights'))

    def reinforce_step(self, session, data, update_model=True, update_baseline=True, use_sgd=False, **kwargs):
        if self.dropout is not None:
            session.run(self.dropout_off)

        batch = self.get_batch(data)
        encoder_inputs, targets, encoder_input_length = batch

        batch_size = targets.shape[1]
        target_length = [self.max_output_len] * batch_size

        input_feed = {
            self.target_length: target_length,
            self.targets: targets,
            self.feed_previous: 1.0,
            self.feed_argmax: False   # sample from softmax
        }

        for i in range(self.encoder_count):
            input_feed[self.encoder_input_length[i]] = encoder_input_length[i]
            input_feed[self.encoder_inputs[i]] = encoder_inputs[i]

        output_feed = {'loss': self.reinforce_loss, 'baseline_loss': self.baseline_loss}

        if update_model:
            output_feed['updates'] = self.sgd_update_op if use_sgd else self.update_op

        if update_baseline:
            output_feed['baseline_updates'] = self.baseline_update_op

        res = session.run(output_feed, input_feed)

        return namedtuple('output', 'loss baseline_loss')(res['loss'], res['baseline_loss'])

    def reinforce_step_bis(self, session, data, update_model=True, update_baseline=True,
                           use_sgd=False, reward_function=None, **kwargs):
        # Same as `reinforce_step` except that reward is computed outside of the TensorFlow graph,
        # which means that we need to do a forward pass and then a backward pass.
        # This is slower, but more powerful than `reinforce_step` as any reward function can be used.

        if self.dropout is not None:
            session.run(self.dropout_off)

        batch = self.get_batch(data)
        encoder_inputs, targets, encoder_input_length = batch

        batch_size = targets.shape[1]
        target_length = [self.max_output_len] * batch_size

        input_feed = {
            self.target_length: target_length,
            self.targets: targets,
            self.feed_previous: 1.0,
            self.feed_argmax: False   # sample from softmax
        }

        for i in range(self.encoder_count):
            input_feed[self.encoder_input_length[i]] = encoder_input_length[i]
            input_feed[self.encoder_inputs[i]] = encoder_inputs[i]

        sampled_output, outputs, rewards_ = session.run([self.sampled_output, self.outputs, self.rewards], input_feed)

        # compute rewards
        targets_ = targets[1:].T
        outputs_ = sampled_output.T

        if reward_function is None:
            reward_function = 'sentence_bleu'

        reward_function = getattr(utils, reward_function)

        time_steps = sampled_output.shape[0]

        rewards = []
        for target, output in zip(targets_, outputs_):
            i, = np.where(output == utils.EOS_ID)  # array of indices whose value is EOS_ID
            if len(i) > 0:
                output = output[:i[0]]

            i, = np.where(target == utils.EOS_ID)
            if len(i) > 0:
                target = target[:i[0]]

            # reward = self.reinforce_reward(output_, target_)
            if self.partial_rewards:
                reward = [reward_function(output[:i + 1], target) for i in range(len(output))]
                reward = [0] + reward
                reward += [reward[-1]] * (time_steps - len(reward) + 1)
                reward = np.array(reward)

                reward = reward[1:] - reward[:-1]
            else:
                reward = reward_function(output, target)

            rewards.append(reward)

        if self.partial_rewards:
            rewards = np.array(rewards).T
        else:
            rewards = np.stack([rewards] * time_steps)

        input_feed[self.rewards] = rewards
        input_feed[self.outputs] = outputs
        input_feed[self.sampled_output] = sampled_output

        output_feed = {'loss': self.reinforce_loss, 'baseline_loss': self.baseline_loss}

        if update_model:
            output_feed['updates'] = self.sgd_update_op if use_sgd else self.update_op

        if update_baseline:
            output_feed['baseline_updates'] = self.baseline_update_op

        res = session.run(output_feed, input_feed)

        return namedtuple('output', 'loss baseline_loss')(res['loss'], res['baseline_loss'])

    def greedy_decoding(self, session, token_ids):
        if self.dropout is not None:
            session.run(self.dropout_off)

        token_ids = [token_ids_ + [[]] for token_ids_ in token_ids]

        batch = self.get_batch(token_ids, decoding=True)
        encoder_inputs, targets, encoder_input_length = batch

        input_feed = {self.targets: targets, self.feed_previous: 1.0}

        for i in range(self.encoder_count):
            input_feed[self.encoder_input_length[i]] = encoder_input_length[i]
            input_feed[self.encoder_inputs[i]] = encoder_inputs[i]

        outputs = session.run(self.outputs, input_feed)

        return np.argmax(outputs, axis=2).T

    def beam_search_decoding(self, session, token_ids, beam_size, ngrams=None, early_stopping=True):
        if not isinstance(session, list):
            session = [session]

        if self.dropout is not None:
            for session_ in session:
                session_.run(self.dropout_off)

        data = [token_ids + [[]]]
        batch = self.get_batch(data, decoding=True)
        encoder_inputs, targets, encoder_input_length = batch
        input_feed = {}

        for i in range(self.encoder_count):
            input_feed[self.encoder_input_length[i]] = encoder_input_length[i]
            input_feed[self.encoder_inputs[i]] = encoder_inputs[i]

        output_feed = [self.encoder_state] + self.attention_states
        res = [session_.run(output_feed, input_feed) for session_ in session]
        state, attn_states = list(zip(*[(res_[0], res_[1:]) for res_ in res]))

        targets = targets[0]  # BOS symbol

        finished_hypotheses = []
        finished_scores = []

        hypotheses = [[]]
        scores = np.zeros([1], dtype=np.float32)

        # for initial state projection
        state = [session_.run(self.beam_tensors.state, {self.encoder_state: state_})
                 for session_, state_ in zip(session, state)]
        output = None

        for i in range(self.max_output_len):
            # each session/model has its own input and output
            # in beam-search decoder, we only feed the first input
            batch_size = targets.shape[0]
            targets = np.reshape(targets, [1, batch_size])
            targets = np.concatenate([targets, np.ones(targets.shape) * utils.EOS_ID])

            input_feed = [
                {self.beam_tensors.state: state_,
                 self.targets: targets,
                 self.target_length: [1] * batch_size,
                }
                for state_ in state
            ]
            
            for feed in input_feed:
                for j in range(self.encoder_count):
                    feed[self.encoder_input_length[j]] = encoder_input_length[j]

            if i > 0:
                for input_feed_, output_ in zip(input_feed, output):
                    input_feed_[self.beam_tensors.output] = output_

            for input_feed_, attn_states_ in zip(input_feed, attn_states):
                for j in range(self.encoder_count):
                    input_feed_[self.attention_states[j]] = attn_states_[j].repeat(batch_size, axis=0)

            output_feed = namedtuple('beam_output', 'output state proba')(
                self.beam_tensors.new_output,
                self.beam_tensors.new_state,
                self.beam_output
            )

            res = [session_.run(output_feed, input_feed_) for session_, input_feed_ in zip(session, input_feed)]

            res_transpose = list(
                zip(*[(res_.output, res_.state, res_.proba) for res_ in res])
            )

            output, state, proba = res_transpose
            # hypotheses, list of tokens ids of shape (beam_size, previous_len)
            # proba, shape=(beam_size, trg_vocab_size)
            # state, shape=(beam_size, cell.state_size)
            # attention_weights, shape=(beam_size, max_len)

            if ngrams is not None:
                lm_score = []
                lm_order = len(ngrams)

                for hypothesis in hypotheses:
                    # not sure about this (should we put <s> at the beginning?)
                    hypothesis = [utils.BOS_ID] + hypothesis
                    history = hypothesis[1 - lm_order:]
                    score_ = []

                    for token_id in range(self.trg_vocab_size):
                        # if token is not in unigrams, this means that either there is something
                        # wrong with the ngrams (e.g. trained on wrong file),
                        # or trg_vocab_size is larger than actual vocabulary
                        if (token_id,) not in ngrams[0]:
                            prob = float('-inf')
                        elif token_id == utils.BOS_ID:
                            prob = float('-inf')
                        else:
                            prob = utils.estimate_lm_score(history + [token_id], ngrams)
                        score_.append(prob)

                    lm_score.append(score_)
                lm_score = np.array(lm_score, dtype=np.float32)
                lm_weight = self.lm_weight or 0.2
                weights = [(1 - lm_weight) / len(session)] * len(session) + [lm_weight]
            else:
                lm_score = np.zeros((1, self.trg_vocab_size))
                weights = None

            proba = [np.maximum(proba_, 1e-10) for proba_ in proba]
            scores_ = scores[:, None] - np.average([np.log(proba_) for proba_ in proba] +
                                                   [lm_score], axis=0, weights=weights)
            scores_ = scores_.flatten()
            flat_ids = np.argsort(scores_)

            token_ids_ = flat_ids % self.trg_vocab_size
            hyp_ids = flat_ids // self.trg_vocab_size

            new_hypotheses = []
            new_scores = []
            new_state = [[] for _ in session]
            new_output = [[] for _ in session]
            new_input = []
            new_beam_size = beam_size

            for flat_id, hyp_id, token_id in zip(flat_ids, hyp_ids, token_ids_):
                hypothesis = hypotheses[hyp_id] + [token_id]
                score = scores_[flat_id]

                if token_id == utils.EOS_ID:
                    # hypothesis is finished, it is thus unnecessary to keep expanding it
                    finished_hypotheses.append(hypothesis)
                    finished_scores.append(score)

                    # early stop: number of possible hypotheses is reduced by one
                    if early_stopping:
                        new_beam_size -= 1
                else:
                    new_hypotheses.append(hypothesis)

                    for session_id, state_, in enumerate(state):
                        new_state[session_id].append(state_[hyp_id])
                        new_output[session_id].append(output[session_id][hyp_id])

                    new_scores.append(score)
                    new_input.append(token_id)

                if len(new_hypotheses) == beam_size:
                    break

            beam_size = new_beam_size
            hypotheses = new_hypotheses
            state = [np.array(new_state_) for new_state_ in new_state]
            output = [np.array(new_output_) for new_output_ in new_output]
            scores = np.array(new_scores)
            targets = np.array(new_input, dtype=np.int32)

            if beam_size <= 0:
                break

        hypotheses += finished_hypotheses
        scores = np.concatenate([scores, finished_scores])

        if self.len_normalization > 0:  # normalize score by length (to encourage longer sentences)
            scores /= [len(hypothesis) ** self.len_normalization for hypothesis in hypotheses]

        # sort best-list by score
        sorted_idx = np.argsort(scores)
        hypotheses = np.array(hypotheses)[sorted_idx].tolist()
        scores = scores[sorted_idx].tolist()
        return hypotheses, scores

    def get_batch(self, data, decoding=False):
        """
        :param data:
        :param decoding: set this parameter to True to output dummy
          data for the decoder side (using the maximum output size)
        :return:
        """
        inputs = [[] for _ in range(self.encoder_count)]
        input_length = [[] for _ in range(self.encoder_count)]
        targets = []

        # maximum input length of each encoder in this batch
        max_input_len = [max(len(data_[i]) for data_ in data) for i in range(self.encoder_count)]
        if self.max_input_len is not None:
            max_input_len = [min(len_, self.max_input_len) for len_ in max_input_len]

        # maximum output length in this batch
        max_output_len = min(max(len(data_[-1]) for data_ in data), self.max_output_len)

        for *src_sentences, trg_sentence in data:
            for i, (encoder, src_sentence) in enumerate(zip(self.encoders, src_sentences)):
                if encoder.binary:
                    # when using binary input, the input sequence is a sequence of vectors,
                    # instead of a sequence of indices
                    pad = np.zeros([encoder.embedding_size], dtype=np.float32)
                else:
                    pad = utils.EOS_ID

                # pad sequences so that all sequences in the same batch have the same length
                src_sentence = src_sentence[:max_input_len[i]]
                encoder_pad = [pad] * (1 + max_input_len[i] - len(src_sentence))

                inputs[i].append(src_sentence + encoder_pad)
                input_length[i].append(len(src_sentence) + 1)

            trg_sentence = trg_sentence[:max_output_len]
            if decoding:
                targets.append([utils.BOS_ID] * self.max_output_len + [utils.EOS_ID])
            else:
                decoder_pad_size = max_output_len - len(trg_sentence) + 1
                trg_sentence = [utils.BOS_ID] + trg_sentence + [utils.EOS_ID] * decoder_pad_size
                targets.append(trg_sentence)

        # convert lists to numpy arrays
        input_length = [np.array(input_length_, dtype=np.int32) for input_length_ in input_length]
        inputs = [
            np.array(inputs_, dtype=(np.float32 if ext in self.binary_input else np.int32))
            for ext, inputs_ in zip(self.encoder_names, inputs)
        ]  # for binary input, the data type is float32

        # starts with BOS and ends with EOS, shape is (time, batch_size)
        targets = np.array(targets).T

        return inputs, targets, input_length
