import os
import sys
import re
import subprocess
import tempfile
import numpy as np
import logging
import struct
import random
import math
import wave
import functools

from translate import pyter
from collections import namedtuple, Counter
from contextlib import contextmanager

# special vocabulary symbols
_BOS = '<S>'
_EOS = '</S>'
_UNK = '<UNK>'
_KEEP = '<KEEP>'
_DEL = '<DEL>'

BOS_ID = 0
EOS_ID = 1
UNK_ID = 2


@contextmanager
def open_files(names, mode='r'):
    """ Safely open a list of files in a context manager.
    Example:
    >>> with open_files(['foo.txt', 'bar.csv']) as (f1, f2):
    ...   pass
    """

    files = []
    try:
        for name_ in names:
            files.append(open(name_, mode=mode))
        yield files
    finally:
        for file_ in files:
            file_.close()


class AttrDict(dict):
    """
    Dictionary whose keys can be accessed as attributes.
    Example:
    >>> d = AttrDict(x=1, y=2)
    >>> d.x
    1
    >>> d.y = 3
    """

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self  # dark magic


def reverse_edits(source, edits):
    src_words = source.split()
    target = []

    i = 0

    for edit in edits.split():
        if edit == _DEL:
            if i < len(src_words):
                i += 1
        elif edit == _KEEP:
            if i < len(src_words):
                target.append(src_words[i])
                i += 1
        else:
            target.append(edit)

    target += src_words[i:]

    return ' '.join(target)


def initialize_vocabulary(vocabulary_path):
    """
    Initialize vocabulary from file.

    We assume the vocabulary is stored one-item-per-line, so a file:
      dog
      cat
    will result in a vocabulary {'dog': 0, 'cat': 1}, and a reversed vocabulary ['dog', 'cat'].

    :param vocabulary_path: path to the file containing the vocabulary.
    :return:
      the vocabulary (a dictionary mapping string to integers), and
      the reversed vocabulary (a list, which reverses the vocabulary mapping).
    """
    if os.path.exists(vocabulary_path):
        rev_vocab = []
        with open(vocabulary_path) as f:
            rev_vocab.extend(f.readlines())
        rev_vocab = [line.rstrip('\n') for line in rev_vocab]
        vocab = dict([(x, y) for (y, x) in enumerate(rev_vocab)])
        return namedtuple('vocab', 'vocab reverse')(vocab, rev_vocab)
    else:
        raise ValueError("vocabulary file %s not found", vocabulary_path)


def sentence_to_token_ids(sentence, vocabulary, character_level=False):
    """
    Convert a string to list of integers representing token-ids.

    For example, a sentence "I have a dog" may become tokenized into
    ["I", "have", "a", "dog"] and with vocabulary {"I": 1, "have": 2,
    "a": 4, "dog": 7"} this function will return [1, 2, 4, 7].

    :param sentence: a string, the sentence to convert to token-ids
    :param vocabulary: a dictionary mapping tokens to integers
    :param character_level: treat sentence as a string of characters, and
        not as a string of words
    :return: a list of integers, the token-ids for the sentence.
    """
    sentence = sentence.rstrip('\n') if character_level else sentence.split()
    return [vocabulary.get(w, UNK_ID) for w in sentence]


def get_filenames(data_dir, extensions, train_prefix, dev_prefix, vocab_prefix,
                  embedding_prefix, lm_file=None, **kwargs):
    """
    Get a bunch of file prefixes and extensions, and output the list of filenames to be used
    by the model.

    :param data_dir: directory where all the the data is stored
    :param extensions: list of file extensions, in the right order (last extension is always the target)
    :param train_prefix: name of the training corpus (usually 'train')
    :param dev_prefix: name of the dev corpus (usually 'dev')
    :param vocab_prefix: prefix of the vocab files (usually 'vocab')
    :param embedding_prefix: prefix of the embedding files
    :param lm_file: full path to a language model file in the ARPA format
    :param kwargs: optional contains an additional 'decode', 'eval' or 'align' parameter
    :return: namedtuple containing the filenames
    """
    train_path = os.path.join(data_dir, train_prefix)
    dev_path = [os.path.join(data_dir, prefix) for prefix in dev_prefix]
    vocab_path = os.path.join(data_dir, vocab_prefix)
    embedding_path = os.path.join(data_dir, embedding_prefix)
    lm_path = lm_file

    train = ['{}.{}'.format(train_path, ext) for ext in extensions]
    dev = [['{}.{}'.format(path, ext) for ext in extensions] for path in dev_path]
    vocab = ['{}.{}'.format(vocab_path, ext) for ext in extensions]
    embeddings = ['{}.{}'.format(embedding_path, ext) for ext in extensions]

    test = kwargs.get('decode')  # empty list means we decode from standard input
    if test is None:
        test = test or kwargs.get('eval')
        test = test or kwargs.get('align')

    filenames = namedtuple('filenames', ['train', 'dev', 'test', 'vocab', 'lm_path', 'embeddings'])
    return filenames(train, dev, test, vocab, lm_path, embeddings)


def sentence_bleu(hypothesis, reference, smoothing=True, order=4, **kwargs):
    """
    Compute sentence-level BLEU score between a translation hypothesis and a reference.
    All reward functions used for REINFORCE should follow this interface.

    :param hypothesis: list of tokens or token ids
    :param reference: list of tokens or token ids
    :param smoothing: apply smoothing (recommended, especially for short sequences)
    :param order: count n-grams up to this value of n.
    :param kwargs: additional (unused) parameters
    :return: BLEU score (float)
    """
    log_score = 0

    if len(hypothesis) == 0:
        return 0

    for i in range(order):
        hyp_ngrams = Counter(zip(*[hypothesis[j:] for j in range(i + 1)]))
        ref_ngrams = Counter(zip(*[reference[j:] for j in range(i + 1)]))

        numerator = sum(min(count, ref_ngrams[bigram]) for bigram, count in hyp_ngrams.items())
        denominator = sum(hyp_ngrams.values())

        if smoothing:
            numerator += 1
            denominator += 1

        score = numerator / denominator

        if score == 0:
            log_score += float('-inf')
        else:
            log_score += math.log(score) / order

    bp = min(1, math.exp(1 - len(reference) / len(hypothesis)))

    return math.exp(log_score) * bp


def corpus_bleu(hypotheses, references, smoothing=False, order=4, **kwargs):
    """
    Computes the BLEU score at the corpus-level between a list of translation hypotheses and references.
    With the default settings, this computes the exact same score as `multi-bleu.perl`.

    All corpus-based evaluation functions should follow this interface.

    :param hypotheses: list of strings
    :param references: list of strings
    :param smoothing: apply +1 smoothing
    :param order: count n-grams up to this value of n. `multi-bleu.perl` uses a value of 4.
    :param kwargs: additional (unused) parameters
    :return: score (float), and summary containing additional information (str)
    """
    total = np.zeros((4,))
    correct = np.zeros((4,))

    hyp_length = 0
    ref_length = 0

    for hyp, ref in zip(hypotheses, references):
        hyp = hyp.split()
        ref = ref.split()

        hyp_length += len(hyp)
        ref_length += len(ref)

        for i in range(order):
            hyp_ngrams = Counter(zip(*[hyp[j:] for j in range(i + 1)]))
            ref_ngrams = Counter(zip(*[ref[j:] for j in range(i + 1)]))

            total[i] += sum(hyp_ngrams.values())
            correct[i] += sum(min(count, ref_ngrams[bigram]) for bigram, count in hyp_ngrams.items())

    if smoothing:
        total += 1
        correct += 1

    scores = correct / total

    score = math.exp(
        sum(math.log(score) if score > 0 else float('-inf') for score in scores) / order
    )

    bp = min(1, math.exp(1 - ref_length / hyp_length))
    bleu = 100 * bp * score

    return bleu, 'penalty={:.3f} ratio={:.3f}'.format(bp, hyp_length / ref_length)


def sentence_ter(hypothesis, reference, **kwargs):
    """
    This is not exactly TER, but 1 - TER,
    which is necessary for this to be a reward function (the higher the better)
    """
    return 1 - pyter.ter(hypothesis, reference)


def corpus_ter(hypotheses, references, **kwargs):
    scores = [pyter.ter(hyp.split(), ref.split()) for hyp, ref in zip(hypotheses, references)]
    score = 100 * sum(scores) / len(scores)

    hyp_length = sum(len(hyp.split()) for hyp in hypotheses)
    ref_length = sum(len(ref.split()) for ref in references)

    return score, 'ratio={:.3f}'.format(hyp_length / ref_length)


def sentence_wer(hypothesis, reference, **kwargs):
    """
    1 - WER
    """
    reference = tuple(reference.split())
    hypothesis = tuple(hypothesis.split())

    return 1 - levenhstein(hypothesis, reference) / len(reference)


def corpus_wer(hypotheses, references, **kwargs):
    scores = [
        levenhstein(tuple(hyp.split()), tuple(ref.split())) / len(ref.split())
        for hyp, ref in zip(hypotheses, references)
    ]

    score = 100 * sum(scores) / len(scores)

    hyp_length = sum(len(hyp.split()) for hyp in hypotheses)
    ref_length = sum(len(ref.split()) for ref in references)

    return score, 'ratio={:.3f}'.format(hyp_length / ref_length)


def corpus_scores(hypotheses, references, **kwargs):
    bleu_score, summary = corpus_bleu(hypotheses, references)
    ter, _ = corpus_ter(hypotheses, references)
    wer, _ = corpus_wer(hypotheses, references)

    return bleu_score, '{} wer={:.2f} ter={:.2f}'.format(summary, wer, ter)


@functools.lru_cache(maxsize=1024)
def levenhstein(src, trg):
    if len(src) == 0:
        return len(trg)
    elif len(trg) == 0:
        return len(src)

    return min(
        int(src[0] != src[0]) + levenhstein(src[1:], trg[1:]),
        1 + levenhstein(src[1:], trg),
        1 + levenhstein(src, trg[1:])
    )


def read_embeddings(embedding_filenames, encoders_and_decoder, load_embeddings,
                    vocabs, norm_embeddings=False):
    for encoder_or_decoder, vocab, filename in zip(encoders_and_decoder,
                                                   vocabs,
                                                   embedding_filenames):
        name = encoder_or_decoder.name
        if not load_embeddings or name not in load_embeddings:
            encoder_or_decoder.embedding = None
            continue

        with open(filename) as file_:
            lines = (line.split() for line in file_)
            _, size_ = next(lines)
            size_ = int(size_)
            assert int(size_) == encoder_or_decoder.embedding_size, 'wrong embedding size'
            embedding = np.zeros((encoder_or_decoder.vocab_size, size_), dtype="float32")

            d = dict((line[0], np.array(map(float, line[1:]))) for line in lines)

        for word, index in vocab.vocab.items():
            if word in d:
                embedding[index] = d[word]
            else:
                embedding[index] = np.random.uniform(-math.sqrt(3), math.sqrt(3), size_)

        if norm_embeddings:  # FIXME
            embedding /= np.linalg.norm(embedding)

        encoder_or_decoder.embedding = embedding


def read_binary_features(filename):
    """
    Reads a binary file containing vector features. First two (int32) numbers correspond to
    number of entries (lines), and dimension of the vectors.
    Each entry starts with a 32 bits integer indicating the number of frames, followed by
    (frames * dimension) 32 bits floats.

    Use `scripts/extract-audio-features.py` to create such a file for audio (MFCCs).

    :param filename: path to the binary file containing the features
    :return: list of arrays of shape (frames, dimension)
    """
    all_feats = []

    with open(filename, 'rb') as f:
        lines, dim = struct.unpack('ii', f.read(8))
        for _ in range(lines):
            frames, = struct.unpack('i', f.read(4))
            n = frames * dim
            feats = struct.unpack('f' * n, f.read(4 * n))
            all_feats.append(list(np.array(feats).reshape(frames, dim)))

    return all_feats


def read_dataset(paths, extensions, vocabs, max_size=None, binary_input=None,
                 character_level=None, sort_by_length=False, max_seq_len=None):
    data_set = []

    line_reader = read_lines(paths, extensions, binary_input=binary_input)
    character_level = character_level or [False] * len(extensions)

    for counter, inputs in enumerate(line_reader, 1):
        if max_size and counter > max_size:
            break
        if counter % 100000 == 0:
            log("  reading data line {}".format(counter))

        inputs = [
            sentence_to_token_ids(input_, vocab.vocab, character_level=char_level)
            if vocab is not None and isinstance(input_, str)
            else input_
            for input_, vocab, ext, char_level in zip(inputs, vocabs, extensions, character_level)
        ]

        if not all(inputs):  # skip empty inputs
            continue
        # skip lines that are too long
        if max_seq_len and any(len(inputs_) > max_seq_len for inputs_ in inputs):
            continue

        data_set.append(inputs)  # TODO: filter too long

    debug('files: {}'.format(' '.join(paths)))
    debug('size: {}'.format(len(data_set)))

    if sort_by_length:
        data_set.sort(key=lambda lines: list(map(len, lines)))

    return data_set


def random_batch_iterator(data, batch_size):
    """
    The most basic form of batch iterator.

    :param data: the dataset to segment into batches
    :param batch_size: the size of a batch
    :return: an iterator which yields random batches (indefinitely)
    """
    while True:
        yield random.sample(data, batch_size)


def cycling_batch_iterator(data, batch_size, shuffle=True, allow_smaller=True):
    """
    Indefinitely cycle through a dataset and yield batches (the dataset is shuffled
    at each new epoch)

    :param data: the dataset to segment into batches
    :param batch_size: the size of a batch
    :return: an iterator which yields batches (indefinitely)
    """
    while True:
        if shuffle:
            random.shuffle(data)

        batch_count = len(data) // batch_size

        if allow_smaller and batch_count * batch_size < len(data):
            batch_count += 1

        for i in range(batch_count):
            yield data[i * batch_size:(i + 1) * batch_size]


def read_ahead_batch_iterator(data, batch_size, read_ahead=10, shuffle=True, allow_smaller=True,
                              mode='standard', **kwargs):
    """
    Same iterator as `cycling_batch_iterator`, except that it reads a number of batches
    at once, and sorts their content according to their size.

    This is useful for training, where all the sequences in one batch need to be padded
     to the same length as the longest sequence in the batch.

    :param data: the dataset to segment into batches
    :param batch_size: the size of a batch
    :param read_ahead: number of batches to read ahead of time and sort (larger numbers
      mean faster training, but less random behavior)
    :return: an iterator which yields batches (indefinitely)
    """
    if mode == 'random':
        iterator = random_batch_iterator(data, batch_size)
    else:
        iterator = cycling_batch_iterator(data, batch_size, shuffle=shuffle, allow_smaller=allow_smaller)

    if read_ahead <= 1:
        while True:
            yield next(iterator)

    while True:
        batches = [next(iterator) for _ in range(read_ahead)]
        data_ = sorted(sum(batches, []), key=lambda lines: len(lines[-1]))
        batches = [data_[i * batch_size:(i + 1) * batch_size] for i in range(read_ahead)]
        if shuffle:
            random.shuffle(batches)
        for batch in batches:
            yield batch


def read_ahead_batch_iterator_blocks(data, batch_size, read_ahead=10, shuffle=True):
    random.shuffle(data)

    while True:
        batch_count = len(data) // batch_size
        batches = [data[i * batch_size:(i + 1) * batch_size] for i in range(batch_count + 1)]

        while True:
            batches_ = batches[:read_ahead]
            batches = batches[read_ahead:]

            if not batches_:
                break

            data_ = sorted(sum(batches_, []), key=lambda lines: len(lines[-1]))
            for i in range(read_ahead):
                batch = data_[i * batch_size:(i + 1) * batch_size]
                if batch:
                    yield batch


def get_batches(data, batch_size, batches=0, allow_smaller=True):
    """
    Segment `data` into a given number of fixed-size batches. The dataset is automatically shuffled.

    This function is for smaller datasets, when you need access to the entire dataset at once (e.g. dev set).
    For larger (training) datasets, where you may want to lazily iterate over batches
    and cycle several times through the entire dataset, prefer batch iterators
    (such as `cycling_batch_iterator`).

    :param data: the dataset to segment into batches (a list of data points)
    :param batch_size: the size of a batch
    :param batches: number of batches to return (0 for the largest possible number)
    :param allow_smaller: allow the last batch to be smaller
    :return: a list of batches (which are lists of `batch_size` data points)
    """
    if not allow_smaller:
        max_batches = len(data) // batch_size
    else:
        max_batches = int(math.ceil(len(data) / batch_size))

    if batches < 1 or batches > max_batches:
        batches = max_batches

    random.shuffle(data)
    batches = [data[i * batch_size:(i + 1) * batch_size] for i in range(batches)]
    return batches


def read_lines(paths, extensions, binary_input=None):
    binary_input = binary_input or [False] * len(extensions)

    if not paths:  # read from stdin (only works with one encoder with text input)
        assert len(extensions) == 1 and not any(binary_input)
        paths = [None]

    iterators = [
        sys.stdin if filename is None else read_binary_features(filename) if binary else open(filename)
        for ext, filename, binary in zip(extensions, paths, binary_input)
    ]

    return zip(*iterators)


def read_ngrams(lm_path, vocab):
    """
    Read a language model from a file in the ARPA format,
    and return it as a list of dicts.

    :param lm_path: full path to language model file
    :param vocab: vocabulary used to map words from the LM to token ids
    :return: one dict for each ngram order, containing mappings from
      ngram (as a sequence of token ids) to (log probability, backoff weight)
    """
    ngram_list = []
    with open(lm_path) as f:
        for line in f:
            line = line.strip()
            if re.match(r'\\\d-grams:', line):
                ngram_list.append({})
            elif not line or line == '\\end\\':
                continue
            elif ngram_list:
                arr = list(map(str.rstrip, line.split('\t')))
                ngram = arr.pop(1)
                ngram_list[-1][ngram] = list(map(float, arr))

    debug('loaded n-grams, order={}'.format(len(ngram_list)))

    ngrams = []
    mappings = {'<s>': _BOS, '</s>': _EOS, '<unk>': _UNK}

    for kgrams in ngram_list:
        d = {}
        for seq, probas in kgrams.items():
            ids = tuple(vocab.get(mappings.get(w, w)) for w in seq.split())
            if any(id_ is None for id_ in ids):
                continue
            d[ids] = probas
        ngrams.append(d)
    return ngrams


def create_logger(log_file=None):
    """
    Initialize global logger and return it.

    :param log_file: log to this file, or to standard output if None
    :return: created logger
    """
    formatter = logging.Formatter(fmt='%(asctime)s %(message)s', datefmt='%m/%d %H:%M:%S')
    if log_file is not None:
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        handler = logging.FileHandler(log_file)
    else:
        handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    return logger


def log(msg, level=logging.INFO):
    logging.getLogger(__name__).log(level, msg)


def debug(msg): log(msg, level=logging.DEBUG)


def warn(msg): log(msg, level=logging.WARN)


def estimate_lm_score(sequence, ngrams):
    """
    Compute the log score of a sequence according to given language model.

    :param sequence: list of token ids
    :param ngrams: list of dicts, as returned by `read_ngrams`
    :return: log probability of `sequence`

    P(w_3 | w_1, w_2) =
        log_prob(w_1 w_2 w_3)             } if (w_1 w_2 w_3) in language model
        P(w_3 | w_2) + backoff(w_1 w_2)   } otherwise
    in case (w_1 w_2) has no backoff weight, a weight of 0.0 is used
    """
    sequence = tuple(sequence)
    order = len(sequence)
    assert 0 < order <= len(ngrams)
    ngrams_ = ngrams[order - 1]

    if sequence in ngrams_:
        return ngrams_[sequence][0]
    else:
        weights = ngrams[order - 2].get(sequence[:-1])
        backoff_weight = weights[1] if weights is not None and len(weights) > 1 else 0.0
        return estimate_lm_score(sequence[1:], ngrams) + backoff_weight


def heatmap(xlabels=None, ylabels=None, weights=None,
            output_file=None, wav_file=None):
    """
    Draw a heatmap showing the alignment between two sequences.

    :param xlabels: input words or None if binary input (use `wav_file` for audio)
    :param ylabels: output words
    :param weights: numpy array of shape (len(xlabels), len(ylabels))
    :param output_file: write the figure to this file, or show it into a window if None
    :param wav_file: plot the waveform of this audio file on the x axis
    """
    from matplotlib import pyplot as plt

    xlabels = xlabels or []
    ylabels = ylabels or []

    if wav_file is None:
        _, ax = plt.subplots()
    else:
        import matplotlib.gridspec as gridspec
        gs = gridspec.GridSpec(2, 1, height_ratios=[1, 6])
        # ax_audio = plt.subplot()
        ax_audio = plt.subplot(gs[0])
        ax = plt.subplot(gs[1])
        from pylab import fromstring
        f = wave.open(wav_file)
        sound_info = f.readframes(-1)
        sound_info = fromstring(sound_info, 'int16')
        ax_audio.plot(sound_info, color='gray')
        ax_audio.xaxis.set_visible(False)
        ax_audio.yaxis.set_visible(False)
        ax_audio.set_frame_on(False)
        ax_audio.set_xlim(right=len(sound_info))

    plt.autoscale(enable=True, axis='x', tight=True)
    ax.pcolor(weights, cmap=plt.cm.Greys)
    ax.set_frame_on(False)
    # plt.colorbar(mappable=heatmap_)

    # put the major ticks at the middle of each cell
    ax.set_yticks(np.arange(weights.shape[0]) + 0.5, minor=False)
    ax.set_xticks(np.arange(weights.shape[1]) + 0.5, minor=False)
    ax.invert_yaxis()
    ax.xaxis.tick_top()

    ax.set_xticklabels(xlabels, minor=False)
    ax.set_yticklabels(ylabels, minor=False)
    ax.tick_params(axis='both', which='both', length=0)

    if wav_file is None:
        plt.xticks(rotation=90, fontsize=20)
    plt.yticks(fontsize=20)
    plt.tight_layout()
    # plt.subplots_adjust(wspace=0, hspace=0)
    # ax.set_aspect('equal')
    ax.grid(False)

    if output_file is None:
        plt.show()
    else:
        plt.savefig(output_file)

def write_attmodel_file(xlabels=None, ylabels=None, weights=None,
output_file=None, wav_file=None):
    """
        :param xlabels: input words or None if binary input (use `wav_file` for audio)
        :param ylabels: output words
        :param weights: numpy array of shape (len(xlabels), len(ylabels))
        :param output_file: write the matrix in this file
        :param wav_file: plot the waveform of this audio file on the x axis
    """
    if not wav_file:
        with open(output_file.replace("svg","txt").replace("jpg","txt"), "w") as outputFile:
            outputFile.write(" \t"+"\t".join(xlabels)+"\n")
            for i in range(0,len(ylabels)):
                outputFile.write(ylabels[i])
                for j in range(0,len(xlabels)):
                    outputFile.write("\t" + str(weights[i][j]))
                outputFile.write("\n")
