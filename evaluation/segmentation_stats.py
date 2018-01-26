# -*- coding: utf-8 -*-

import sys
import codecs
from itertools import chain

class Stats:
    def __init__(self, path, name):
        self.name = name
        self.tokens = self.read_file(path)
        self.num_tokens = len(self.tokens)
        self.types = self.get_types(self.tokens)
        self.vocab_size = len(self.types)
        self.avg_word_length = self.get_avg_length(self.tokens, self.num_tokens)
        self.short = self.get_f(self.types, min)
        self.long = self.get_f(self.types, max)

    def read_file(self, path):
        sentences = [line.strip().split(" ") for line in codecs.open(path,"r","UTF-8")]
        return list(chain.from_iterable(sentences))

    def get_types(self, sentences_list):
        return list(set(sentences_list))

    def get_avg_length(self, types, size):
        avg = 0.0
        for t in types:
            avg += len(t)
        return (avg / size)

    def get_f(self, words_list, f):
        w_min = words_list[0]
        for word in words_list:
            if f(len(word),len(w_min)) == len(word):
                w_min = word
        return w_min

def write_output(path, seg, gold):
    with codecs.open(path, "w") as outputFile:
        outputFile.write("\t".join(["","num_tokens", "vocab_size", "avg_word_length", "shortest_word", "longest_word"]) + "\n")
        for stats in [seg,gold]:
            outputFile.write("\t".join([str(stats.name), str(stats.num_tokens), str(stats.vocab_size), str(stats.avg_word_length), str(len(stats.short)), str(len(stats.long))]) + "\n")
        correct_types = set(gold.types).intersection(seg.types)
        outputFile.write("Vocabulary Intersection: " + str(len(correct_types)) + "\n")


def main():
    stats_file = sys.argv[3]
    generated = Stats(sys.argv[1],"generated")
    gold = Stats(sys.argv[2], "gold_standard")
    write_output(stats_file, generated, gold)
    # avg tokens per sentence!!!!
    #file for plotting zipf
    if(len(sys.argv) > 4):
        zipf_out = sys.argv[4]




if __name__ == '__main__':
    main()
