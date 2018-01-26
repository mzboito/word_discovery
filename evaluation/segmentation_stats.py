# -*- coding: utf-8 -*-

import sys
import codecs
from itertools import chain

class Stats:
    def __init__(self, path, name):
        self.name = name
        self.sentences = self.read_file(path)
        self.tokens = self.get_tokens()
        self.types = self.get_types()
        self.num_tokens = len(self.tokens)
        self.vocab_size = len(self.types)
        self.avg_word_length = self.get_avg_length()
        self.avg_tokens_per_sentence = self.get_avg_tokens()
        self.short = self.get_f(min)
        self.long = self.get_f(max)
        self.words_dict = self.get_frequency_count()

    def read_file(self, path):
        return [line.strip().split(" ") for line in codecs.open(path,"r","UTF-8")]

    def get_tokens(self):
        return list(chain.from_iterable(self.sentences))

    def get_types(self):
        return list(set(self.tokens))

    def get_avg_length(self):
        avg = 0.0
        for t in self.types:
            avg += len(t)
        return (avg / self.vocab_size)

    def get_avg_tokens(self):
        sum_s = 0.0
        for sentence in self.sentences:
            sum_s += len(sentence)
        return (sum_s / len(self.sentences))

    def get_f(self, f):
        words_list = self.types
        w_m = words_list[0]
        for word in words_list:
            if f(len(word),len(w_m)) == len(word):
                w_m = word
        return w_m

    def get_frequency_count(self):
        words_dict = dict(zip([],[]))
        for token in self.tokens:
            if words_dict.get(token):
                words_dict[token] += 1
            else: #key not found
                words_dict[token] = 1
        return words_dict

def write_stats(path, seg, gold):
    with open(path, "w") as outputFile:
        outputFile.write("\t".join(["","num_tokens", "vocab_size", "avg_word_length", "avg_tokens_per_sentence", "shortest_word", "longest_word"]) + "\n")
        for stats in [seg,gold]:
            outputFile.write("\t".join([str(stats.name), str(stats.num_tokens), str(stats.vocab_size), str(stats.avg_word_length), str(stats.avg_tokens_per_sentence),str(len(stats.short)), str(len(stats.long))]) + "\n")
        correct_types = set(gold.types).intersection(seg.types)
        outputFile.write("Vocabulary Intersection: " + str(len(correct_types)) + "\n")

def write_vocab(path, stats):
    with codecs.open(path,"w", "UTF-8") as outputFile:
        for key, value in sorted(stats.words_dict.iteritems(), key=lambda (k,v): (v,k), reverse=True):
            outputFile.write("\t".join([key, str(stats.words_dict[key])]) + "\n")

def main():
    stats_folder = sys.argv[3]
    generated = Stats(sys.argv[1],"generated")
    gold = Stats(sys.argv[2], "gold_standard")
    write_stats(stats_folder + "/segmentation_stats", generated, gold)
    #generates vocab file
    write_vocab(stats_folder + "/" + sys.argv[1].split("/")[-1] + ".vocab", generated)
    write_vocab(stats_folder + "/" + sys.argv[2].split("/")[-1] + ".vocab", gold)

if __name__ == '__main__':
    main()
