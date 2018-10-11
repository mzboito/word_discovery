# -*- coding: utf-8 -*-

import sys
import codecs
from itertools import chain

class Stats:
    def __init__(self, path):
        self.path = path
        self.name = self.path.split("/")[-1]
        self.sentences = self.read_file()
        self.tokens = self.get_tokens()
        self.types = self.get_types()
        self.num_tokens = len(self.tokens)
        self.vocab_size = len(self.types)
        self.avg_word_length = self.get_avg_length()
        self.avg_tokens_per_sentence = self.get_avg_tokens()
        self.short = self.get_f(min)
        self.long = self.get_f(max)
        self.words_dict = self.get_frequency_count()

    def read_file(self):
        return [line.strip().split(" ") for line in codecs.open(self.path,"r","UTF-8")]

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

def write_stats(segmentation):
    with open(segmentation.path + ".stats", "w") as outputFile:
        outputFile.write("\t".join(["","num_tokens", "vocab_size", "avg_word_length", "avg_tokens_per_sentence", "shortest_word", "longest_word"]) + "\n")
        outputFile.write("\t".join([str(segmentation.name), str(segmentation.num_tokens), str(segmentation.vocab_size), str(segmentation.avg_word_length), str(segmentation.avg_tokens_per_sentence),str(len(segmentation.short)), str(len(segmentation.long))]) + "\n")

def write_vocab(segmentation):
    with codecs.open(segmentation.path +".vocab","w", "UTF-8") as outputFile:
        for key, value in sorted(segmentation.words_dict.iteritems(), key=lambda (k,v): (v,k), reverse=True):
            outputFile.write("\t".join([key, str(segmentation.words_dict[key])]) + "\n")

def main():
    if len(sys.argv) < 2:
        print "USAGE:\n python segmentation_stats.py <list of files>\n"
        exit(1)
    
    segmentations = [Stats(file_path) for file_path in sys.argv[1:]]
    for segmentation in segmentations:
        write_stats(segmentation)
        write_vocab(segmentation)
    
    #stats_folder = sys.argv[3]
    #generated = Stats(sys.argv[1],"generated")
    #gold = Stats(sys.argv[2], "gold_standard")
            #for stats in [seg,gold]:
        #correct_types = set(gold.types).intersection(seg.types)
        #outputFile.write("Vocabulary Intersection: " + str(len(correct_types)) + "\n")
    #write_stats(stats_folder + "/" + sys.argv[1].split("/")[-1] +".segmentation_stats", generated, gold)
    #write_vocab(stats_folder + "/" + sys.argv[2].split("/")[-1] + ".vocab", gold)

if __name__ == '__main__':
    main()
