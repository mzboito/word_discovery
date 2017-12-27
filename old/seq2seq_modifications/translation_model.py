import tensorflow as tf
import os
import pickle
import time
import sys
import math
import numpy as np
import shutil
from translate import utils
from translate.seq2seq_model import Seq2SeqModel


class BaseTranslationModel(object):
    def __init__(self, name, checkpoint_dir, keep_best=1):
        self.name = name
        self.keep_best = keep_best
        self.checkpoint_dir = checkpoint_dir
        self.saver = None
        self.global_step = None

    def manage_best_checkpoints(self, step, score):
        score_filename = os.path.join(self.checkpoint_dir, 'scores.txt')
        # try loading previous scores
        try:
            with open(score_filename) as f:
                # list of pairs (score, step)
                scores = [(float(line.split()[0]), int(line.split()[1])) for line in f]
        except IOError:
            scores = []

        if any(step_ >= step for _, step_ in scores):
            utils.warn('inconsistent scores.txt file')

        best_scores = sorted(scores, reverse=True)[:self.keep_best]

        def full_path(filename):
            return os.path.join(self.checkpoint_dir, filename)

        if any(score_ < score for score_, _ in best_scores) or not best_scores:
            # if this checkpoint is in the top, save it under a special name

            prefix = 'translate-{}'.format(step)
            dest_prefix = 'best-{}'.format(step)

            for filename in os.listdir(self.checkpoint_dir):
                if filename.startswith(prefix):
                    dest_filename = filename.replace(prefix, dest_prefix)
                    shutil.copy(full_path(filename), full_path(dest_filename))

                    # also copy to `best` if this checkpoint is the absolute best
                    if all(score_ < score for score_, _ in best_scores):
                        dest_filename = filename.replace(prefix, 'best')
                        shutil.copy(full_path(filename), full_path(dest_filename))

            best_scores = sorted(best_scores + [(score, step)], reverse=True)

            for _, step_ in best_scores[self.keep_best:]:
                # remove checkpoints that are not in the top anymore
                prefix = 'best-{}'.format(step_)
                for filename in os.listdir(self.checkpoint_dir):
                    if filename.startswith(prefix):
                        os.remove(full_path(filename))

        # save bleu scores
        scores.append((score, step))

        with open(score_filename, 'w') as f:
            for score_, step_ in scores:
                f.write('{:.2f} {}\n'.format(score_, step_))

    def initialize(self, sess, checkpoints=None, reset=False, reset_learning_rate=False, **kwargs):
        self.saver = tf.train.Saver(max_to_keep=3, keep_checkpoint_every_n_hours=5, sharded=False)

        sess.run(tf.global_variables_initializer())
        blacklist = ['dropout_keep_prob']

        if reset_learning_rate or reset:
            blacklist.append('learning_rate')
        if reset:
            blacklist.append('global_step')
        
        if checkpoints:  # load partial checkpoints
            for checkpoint in checkpoints:  # checkpoint files to load
                load_checkpoint(sess, None, checkpoint, blacklist=blacklist)
        elif not reset:
            load_checkpoint(sess, self.checkpoint_dir, blacklist=blacklist)

    def save(self, sess):
        save_checkpoint(sess, self.saver, self.checkpoint_dir, self.global_step)


class TranslationModel(BaseTranslationModel):
    def __init__(self, name, encoders, decoder, checkpoint_dir, learning_rate, learning_rate_decay_factor, batch_size,
                 keep_best=1, load_embeddings=None, max_input_len=None, **kwargs):
        super(TranslationModel, self).__init__(name, checkpoint_dir, keep_best)

        self.batch_size = batch_size
        self.src_ext = [encoder.get('ext') or encoder.name for encoder in encoders]
        self.trg_ext = decoder.get('ext') or decoder.name
        self.extensions = self.src_ext + [self.trg_ext]
        self.max_input_len = max_input_len

        encoders_and_decoder = encoders + [decoder]
        self.binary_input = [encoder_or_decoder.binary for encoder_or_decoder in encoders_and_decoder]
        self.character_level = [encoder_or_decoder.character_level for encoder_or_decoder in encoders_and_decoder]

        self.learning_rate = tf.Variable(learning_rate, trainable=False, name='learning_rate', dtype=tf.float32)
        self.learning_rate_decay_op = self.learning_rate.assign(self.learning_rate * learning_rate_decay_factor)

        with tf.device('/cpu:0'):
            self.global_step = tf.Variable(0, trainable=False, name='global_step')

        self.filenames = utils.get_filenames(extensions=self.extensions, **kwargs)
        # TODO: check that filenames exist
        utils.debug('reading vocabularies')
        self._read_vocab()

        for encoder_or_decoder, vocab in zip(encoders + [decoder], self.vocabs):
            if encoder_or_decoder.vocab_size <= 0 and vocab is not None:
                encoder_or_decoder.vocab_size = len(vocab.reverse)

        # this adds an `embedding' attribute to each encoder and decoder
        utils.read_embeddings(self.filenames.embeddings, encoders + [decoder], load_embeddings, self.vocabs)

        # main model
        utils.debug('creating model {}'.format(name))
        self.seq2seq_model = Seq2SeqModel(encoders, decoder, self.learning_rate, self.global_step,
                                          max_input_len=max_input_len, **kwargs)

        self.batch_iterator = None
        self.dev_batches = None
        self.train_size = None
        self.use_sgd = False

    def read_data(self, max_train_size, max_dev_size, read_ahead=10, batch_mode='standard', shuffle=True, **kwargs):
        utils.debug('reading training data')
        train_set = utils.read_dataset(self.filenames.train, self.extensions, self.vocabs, max_size=max_train_size,
                                       binary_input=self.binary_input, character_level=self.character_level,
                                       max_seq_len=self.max_input_len)
        self.train_size = len(train_set)
        self.batch_iterator = utils.read_ahead_batch_iterator(train_set, self.batch_size, read_ahead=read_ahead,
                                                              mode=batch_mode, shuffle=shuffle)

        utils.debug('reading development data')
        dev_sets = [
            utils.read_dataset(dev, self.extensions, self.vocabs, max_size=max_dev_size,
                               binary_input=self.binary_input, character_level=self.character_level)
            for dev in self.filenames.dev
        ]
        # subset of the dev set whose perplexity is periodically evaluated
        self.dev_batches = [utils.get_batches(dev_set, batch_size=self.batch_size) for dev_set in dev_sets]

    def _read_vocab(self):
        # don't try reading vocabulary for encoders that take pre-computed features
        self.vocabs = [
            utils.initialize_vocabulary(vocab_path) if not binary else None
            for ext, vocab_path, binary in zip(self.extensions, self.filenames.vocab, self.binary_input)
        ]
        self.src_vocab = self.vocabs[:-1]
        self.trg_vocab = self.vocabs[-1]
        self.ngrams = self.filenames.lm_path and utils.read_ngrams(self.filenames.lm_path, self.trg_vocab.vocab)

    def train(self, *args, **kwargs):
        raise NotImplementedError('use MultiTaskModel')

    def train_step(self, sess, loss_function='xent', reward_function=None):
        if loss_function == 'reinforce':
            fun = self.seq2seq_model.reinforce_step_bis
        else:
            fun = self.seq2seq_model.step

        return fun(sess, next(self.batch_iterator), update_model=True, update_baseline=True, use_sgd=self.use_sgd,
                   reward_function=reward_function)

    def baseline_step(self, sess, reward_function=None):
        return self.seq2seq_model.reinforce_step_bis(sess,
                                                     next(self.batch_iterator),
                                                     update_model=False,
                                                     update_baseline=True,
                                                     reward_function=reward_function).baseline_loss

    def eval_step(self, sess):
        # compute perplexity on dev set
        for dev_batches in self.dev_batches:
            eval_loss = sum(
                self.seq2seq_model.step(sess, batch, update_model=False, update_baseline=False).loss * len(batch)
                for batch in dev_batches
            )
            eval_loss /= sum(map(len, dev_batches))

            utils.log("  eval: loss {:.2f}".format(eval_loss))

    def _decode_sentence(self, sess, sentence_tuple, beam_size=1, remove_unk=False, early_stopping=True):
        return next(self._decode_batch(sess, [sentence_tuple], beam_size, remove_unk, early_stopping))

    def _decode_batch(self, sess, sentence_tuples, batch_size, beam_size=1, remove_unk=False, early_stopping=True,
                      use_edits=False):
        beam_search = beam_size > 1 or isinstance(sess, list)

        if beam_search:
            batch_size = 1

        if batch_size == 1:
            batches = ([sentence_tuple] for sentence_tuple in sentence_tuples)   # lazy
        else:
            batch_count = int(math.ceil(len(sentence_tuples) / batch_size))
            batches = [sentence_tuples[i * batch_size:(i + 1) * batch_size] for i in range(batch_count)]

        def map_to_ids(sentence_tuple):
            token_ids = [
                utils.sentence_to_token_ids(sentence, vocab.vocab, character_level=char_level)
                if vocab is not None else sentence  # when `sentence` is not a sentence but a vector...
                for vocab, sentence, char_level in zip(self.vocabs, sentence_tuple, self.character_level)
            ]
            return token_ids

        for batch in batches:
            token_ids = list(map(map_to_ids, batch))

            if beam_search:
                hypotheses, _ = self.seq2seq_model.beam_search_decoding(sess, token_ids[0], beam_size,
                                                                        ngrams=self.ngrams,
                                                                        early_stopping=early_stopping)
                batch_token_ids = [hypotheses[0]]  # first hypothesis is the highest scoring one

            else:
                batch_token_ids = self.seq2seq_model.greedy_decoding(sess, token_ids)

            for src_tokens, trg_token_ids in zip(batch, batch_token_ids):
                trg_token_ids = list(trg_token_ids)

                if utils.EOS_ID in trg_token_ids:
                    trg_token_ids = trg_token_ids[:trg_token_ids.index(utils.EOS_ID)]

                trg_tokens = [self.trg_vocab.reverse[i] if i < len(self.trg_vocab.reverse) else utils._UNK
                              for i in trg_token_ids]

                if use_edits:
                    trg_tokens = utils.reverse_edits(src_tokens[0], ' '.join(trg_tokens)).split()

                if remove_unk:
                    trg_tokens = [token for token in trg_tokens if token != utils._UNK]

                if self.character_level[-1]:
                    yield ''.join(trg_tokens)
                else:
                    yield ' '.join(trg_tokens).replace('@@ ', '')  # merge subword units

    def align(self, sess, output=None, wav_files=None, **kwargs):
        if len(self.src_ext) != 1:
            raise NotImplementedError

        if len(self.filenames.test) != len(self.extensions):
            raise Exception('wrong number of input files')

        for line_id, lines in enumerate(utils.read_lines(self.filenames.test, self.extensions, self.binary_input)):
            token_ids = [
                utils.sentence_to_token_ids(sentence, vocab.vocab, character_level=char_level)
                if vocab is not None else sentence
                for vocab, sentence, char_level in zip(self.vocabs, lines, self.character_level)
            ]

            _, weights = self.seq2seq_model.step(sess, data=[token_ids], forward_only=True, align=True,
                                                 update_model=False)
            trg_tokens = [self.trg_vocab.reverse[i] if i < len(self.trg_vocab.reverse) else utils._UNK
                          for i in token_ids[-1]]

            weights = weights.squeeze()[:len(trg_tokens),:len(token_ids[0])].T
            max_len = weights.shape[0]

            if self.binary_input[0]:
                src_tokens = None
            else:
                src_tokens = lines[0].split()[:max_len]

            if wav_files is not None:
                wav_file = wav_files[line_id]
            else:
                wav_file = None

            output_file = '{}.{}.jpg'.format(output, line_id + 1) if output is not None else None
            #utils.heatmap(src_tokens, trg_tokens, weights.T, wav_file=wav_file, output_file=output_file)		
            utils.write_attmodel_file(src_tokens, trg_tokens, weights.T, wav_file=wav_file, output_file=output_file)

    def decode(self, sess, beam_size, output=None, remove_unk=False, early_stopping=True, use_edits=False, **kwargs):
        utils.log('starting decoding')

        # empty `test` means that we read from standard input, which is not possible with multiple encoders
        assert len(self.src_ext) == 1 or self.filenames.test
        # we can't read binary data from standard input
        assert self.filenames.test or self.src_ext[0] not in self.binary_input
        # check that there is the right number of files for decoding
        assert not self.filenames.test or len(self.filenames.test) == len(self.src_ext)

        output_file = None
        try:
            output_file = sys.stdout if output is None else open(output, 'w')

            lines = utils.read_lines(self.filenames.test, self.src_ext, self.binary_input)

            if self.filenames.test is None:   # interactive mode
                batch_size = 1
            else:
                batch_size = self.batch_size
                lines = list(lines)

            hypothesis_iter = self._decode_batch(sess, lines, batch_size, beam_size=beam_size,
                                                 early_stopping=early_stopping, remove_unk=remove_unk,
                                                 use_edits=use_edits)

            for hypothesis in hypothesis_iter:
                output_file.write(hypothesis + '\n')
                output_file.flush()
        finally:
            if output_file is not None:
                output_file.close()

    def evaluate(self, sess, beam_size, score_function, on_dev=True, output=None, remove_unk=False, max_dev_size=None,
                 script_dir='scripts', early_stopping=True, use_edits=False, **kwargs):
        """
        :param score_function: name of the scoring function used to score and rank models
          (typically 'bleu_score')
        :param on_dev: if True, evaluate the dev corpus, otherwise evaluate the test corpus
        :param output: save the hypotheses to this file
        :param remove_unk: remove the UNK symbols from the output
        :param max_dev_size: maximum number of lines to read from dev files
        :param script_dir: parameter of scoring functions
        :return: scores of each corpus to evaluate
        """
        utils.log('starting decoding')
        assert on_dev or len(self.filenames.test) == len(self.extensions)

        filenames = self.filenames.dev if on_dev else [self.filenames.test]

        # convert `output` into a list, for zip
        if isinstance(output, str):
            output = [output]
        elif output is None:
            output = [None] * len(filenames)

        scores = []

        for filenames_, output_ in zip(filenames, output):  # evaluation on multiple corpora
            lines = list(utils.read_lines(filenames_, self.extensions, self.binary_input))
            if on_dev and max_dev_size:
                lines = lines[:max_dev_size]

            hypotheses = []
            references = []

            output_file = None

            try:
                if output_ is not None:
                    output_file = open(output_, 'w')

                *src_sentences, trg_sentences = zip(*lines)
                src_sentences = list(zip(*src_sentences))

                hypothesis_iter = self._decode_batch(sess, src_sentences, self.batch_size, beam_size=beam_size,
                                                     early_stopping=early_stopping, remove_unk=remove_unk,
                                                     use_edits=use_edits)
                for sources, hypothesis, reference in zip(src_sentences, hypothesis_iter, trg_sentences):
                    if use_edits:
                        # main_source = sources[0]
                        # hypothesis = utils.reverse_edits(main_source, hypothesis)
                        reference = utils.reverse_edits(sources[0], reference)

                    hypotheses.append(hypothesis)
                    references.append(reference.strip().replace('@@ ', ''))

                    if output_file is not None:
                        output_file.write(hypothesis + '\n')
                        output_file.flush()

            finally:
                if output_file is not None:
                    output_file.close()

            # default scoring function is utils.bleu_score
            score, score_summary = getattr(utils, score_function)(hypotheses, references, script_dir=script_dir)

            # print the scoring information
            score_info = []
            if self.name is not None:
                score_info.append(self.name)
            score_info.append('score={:.2f}'.format(score))
            if score_summary:
                score_info.append(score_summary)

            utils.log(' '.join(map(str, score_info)))
            scores.append(score)

        return scores


def load_checkpoint(sess, checkpoint_dir, filename=None, blacklist=()):
    """ `checkpoint_dir` should be unique to this model
    if `filename` is None, we load last checkpoint, otherwise
      we ignore `checkpoint_dir` and load the given checkpoint file.
    """
    if filename is None:
        # load last checkpoint
        ckpt = tf.train.get_checkpoint_state(checkpoint_dir)
        if ckpt is not None:
            filename = ckpt.model_checkpoint_path
    else:
        checkpoint_dir = os.path.dirname(filename)

    var_file = os.path.join(checkpoint_dir, 'vars.pkl')

    if os.path.exists(var_file):
        with open(var_file, 'rb') as f:
            var_names = pickle.load(f)
            variables = [var for var in tf.global_variables() if var.name in var_names]
    else:
        variables = tf.global_variables()

    # remove variables from blacklist
    variables = [var for var in variables if not any(prefix in var.name for prefix in blacklist)]

    if filename is not None:
        utils.log('reading model parameters from {}'.format(filename))
        tf.train.Saver(variables).restore(sess, filename)

        utils.debug('retrieved parameters ({})'.format(len(variables)))
        for var in variables:
            utils.debug('  {} {}'.format(var.name, var.get_shape()))


def save_checkpoint(sess, saver, checkpoint_dir, step=None, name=None):
    """ `checkpoint_dir` should be unique to this model """
    var_file = os.path.join(checkpoint_dir, 'vars.pkl')
    name = name or 'translate'

    if not os.path.exists(checkpoint_dir):
        utils.log("creating directory {}".format(checkpoint_dir))
        os.makedirs(checkpoint_dir)

    with open(var_file, 'wb') as f:
        var_names = [var.name for var in tf.global_variables()]
        pickle.dump(var_names, f)

    utils.log('saving model to {}'.format(checkpoint_dir))
    checkpoint_path = os.path.join(checkpoint_dir, name)
    saver.save(sess, checkpoint_path, step, write_meta_graph=False)

    utils.log('finished saving model')
