# -*- coding: utf-8 -*-

import sys
import codecs
import argparse
import itertools
from Scoring import Sentences

def get_evaluation_parser(parser):
    parser.add_argument('--segmentation', type=str, nargs='?', help='path for generated segmentation')
    parser.add_argument('--gold', type=str, nargs='?', help='path for gold standard file')
    parser.add_argument('--output', type=str, nargs='?', help='name of the output file')
    return parser

def read_file(inputPath):
    return [line.strip("\n") if line[0]!=" " else line[1:].strip("\n") for line in codecs.open(inputPath, "r", "UTF-8")]

def write_evaluation_file(outputPath, scores):
    types, tokens, boundaries = scores
    with open(outputPath, "w") as outputFile:
        outputFile.write("\tP\tR\tF\n")
        print("\tP\tR\tF")
        outputFile.write("TOKENS\t")
        print("TOKENS\t%2.2f\t%2.2f\t%2.2f" % (tokens[1], tokens[0], tokens[2]))
        outputFile.write("%2.2f\t%2.2f\t%2.2f\n" % (tokens[1], tokens[0], tokens[2]))
        outputFile.write("TYPES\t")
        print("TYPES\t%2.2f\t%2.2f\t%2.2f" % (types[1], types[0], types[2]))
        outputFile.write("%2.2f\t%2.2f\t%2.2f\n" % (types[1], types[0], types[2]))
        outputFile.write("BOUNDARIES\t")
        print("BOUNDARIES\t%2.2f\t%2.2f\t%2.2f" % (boundaries[1], boundaries[0], boundaries[2]))
        outputFile.write("%2.2f\t%2.2f\t%2.2f\n" % (boundaries[1], boundaries[0], boundaries[2]))

def recall(correct, sizeGold):
    return (correct / sizeGold) * 100

def precision(correct, totalFound):
    return (correct / totalFound) * 100

def fscore(recall, precision):
    return (2.0*recall*precision / (precision + recall))

def score(correct, sizeSeg, sizeGold):
    p = precision(correct, sizeSeg)
    r = recall(correct, sizeGold)
    return [r, p, fscore(r, p)]

def token_eval(corpus):
    correct, totalSeg, totalGold = corpus.tokens_score()
    return score(correct, totalSeg, totalGold)

def type_eval(corpus):
    correct, totalSeg, totalGold = corpus.types_score()
    return score(correct, totalSeg, totalGold)

def boundary_eval(corpus):
    correctBoundaries, boundariesSeg, boundariesGold = corpus.boundary_score()
    print(correctBoundaries, boundariesSeg, boundariesGold)
    return score(correctBoundaries, boundariesSeg, boundariesGold)

def _evaluate(segmentation, gold):
    s = Sentences(gold,segmentation)
    tokens_score = token_eval(s)
    types_score = type_eval(s)
    boundaries_score = boundary_eval(s)
    return [types_score, tokens_score, boundaries_score]

def evaluate(args):
    segmentation = read_file(args.segmentation)
    gold = read_file(args.gold)
    assert len(segmentation) == len(gold)
    scores = _evaluate(segmentation, gold)
    write_evaluation_file(args.output, scores)

if __name__ == '__main__':
    parser = get_evaluation_parser(argparse.ArgumentParser())
    args = parser.parse_args()
    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(1)
    evaluate(args)
