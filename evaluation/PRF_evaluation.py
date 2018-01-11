# -*- coding: utf-8 -*-

import sys


def print_usage():
    print "PRF evaluation\n"
    print "arg1: generated segmentation\narg2: gold segmentation\narg3: output file\n"

def readFile(inputPath):
    return [line.strip("\n") for line in codecs.open(inputPath, "r", "UTF-8")]

def evaluate(generated_seg, gold_seg):
    tokens = evaluate_tokens(generated_seg, gold_seg)
    types = evaluate_types(generated_seg, gold_seg)
    return [tokens, types]

def evaluate_tokens(generated_seg, gold_seg):

    for i in range(0, len(gold_seg)):
        line_tokens = len(gold_seg[i].split(" ")) #number of tokens in that line
        line_generated = len(generated_seg[i].split(" ")) #same
        correctlySegmented = getScore(mboshiGold[i], mboshiUnsupervised[i]) #number of tokens found



def evaluate_types(generated_seg, gold_seg):
    pass

def write_output(metrics, output_name):
    with open(output_name,"w") as output_file:
        output_file.write("\tPRECISION\tRECALL\tF-SCORE\n")
        output_file.write("\t".join("TYPES", str(metrics[1][0]), str(metrics[1][1]), str(metrics[1][2]))+"\n")
        output_file.write("\t".join("TOKENS", str(metrics[0][0]), str(metrics[0][1]), str(metrics[0][2]))+"\n")

def main():
    if len(sys.argv) > 4:
        generated_seg = readFile(sys.argv[1])
        gold_seg = readFile(sys.argv[2])
        output_name = sys.argv[3]
        metrics = evaluate(generated_seg, gold_seg)
        write_output(metrics, output_name)
    else:
        print_usage()
        sys.exit(1)



if __name__ == '__main__':
    main()
