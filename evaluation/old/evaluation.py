# -*- coding: utf-8 -*-

import sys
import codecs
import argparse
import itertools
from boundary import Sentences, Sentence, Token

def get_evaluation_parser(parser):
    parser.add_argument('--segmentation', type=str, nargs='?', help='path for generated segmentation')
    parser.add_argument('--gold', type=str, nargs='?', help='path for gold standard file')
    parser.add_argument('--output', type=str, nargs='?', help='name of the output file')
    return parser

def read_file(inputPath):
    return [line.strip("\n") if line[0]!=" " else line[1:].strip("\n") for line in codecs.open(inputPath, "r", "UTF-8")]

def write_evaluation_file(outputPath, scores):
    types = scores[0]
    tokens = scores[1]
    boundaries = scores[2]
    with open(outputPath, "w") as outputFile:
        outputFile.write("\tP\tR\tF\n")
        outputFile.write("TOKENS\t")
        outputFile.write("%2.2f\t%2.2f\t%2.2f\n" % (tokens[1], tokens[0], tokens[2]))
        outputFile.write("TYPES\t")
        outputFile.write("%2.2f\t%2.2f\t%2.2f\n" % (types[1], types[0], types[2]))
        outputFile.write("BOUNDARIES\t")
        outputFile.write("%2.2f\t%2.2f\t%2.2f\n" % (boundaries[1], boundaries[0], boundaries[2]))

def recall(correct, sizeGold):
    return (float(correct) / sizeGold) * 100

def precision(correct, totalFound):
    return (float(correct) / totalFound) * 100

def fscore(recall, precision):
    return (2.0*recall*precision / (precision + recall))

def score(correct, sizeSeg, sizeGold):
    p = precision(correct, sizeSeg)
    r = recall(correct, sizeGold)
    return [r, p, fscore(r, p)]

def get_tokens_score(segmentation, gold):
    trueTokens = gold.strip("\n").split(" ")
    segTokens = segmentation.strip("\n").split(" ")
    score = 0
    for token in segTokens: #for each generated token
        if token in trueTokens: #check if it is on the true tokens list
            trueTokens.remove(token) #avoid multiples matches for the same token 
            score += 1
    return score

def get_tokens(set1):
    tokens = [line.strip("\n").split(" ") for line in set1]
    return list(itertools.chain.from_iterable(tokens))

def get_types(set1):
    tokens = get_tokens(set1)
    return list(set(tokens)) #remove dups

def count_boundaries(set1):
    count = 0
    for line in set1:
        count += line.count(" ")
    return count

def tokens_intersection(segmentation, gold): #Intersection on sentence level to avoid scoring right tokens in wrong places
    correctly_segmented = 0
    for i in range(0, len(gold)):
        correctly_segmented += get_tokens_score(segmentation[i], gold[i]) #number of tokens found
    return correctly_segmented

def types_intersection(segmentation, gold):
    return len([t for t in segmentation if t in gold])

def token_eval(segmentation, gold):
    tokensGold = len(get_tokens(gold))
    tokensSeg = len(get_tokens(segmentation))
    correctTokens = tokens_intersection(segmentation, gold) #INTERSECTION ON SENTENCE LEVEL! 
    print(correctTokens, tokensSeg, tokensGold)
    return score(correctTokens, tokensSeg, tokensGold)

def type_eval(segmentation, gold):
    typesGold = get_types(gold)
    typesSeg = get_types(segmentation)
    correctTypes = types_intersection(typesSeg, typesGold)
    return score(correctTypes, len(typesSeg), len(typesGold))

def boundary_eval(segmentation, gold):
    s = Sentences(gold,segmentation)
    correctBoundaries, boundariesSeg, boundariesGold = s.boundary_score()
    return score(correctBoundaries, boundariesSeg, boundariesGold)

def _evaluate(segmentation, gold):
    types_score = type_eval(segmentation,gold)
    tokens_score = token_eval(segmentation,gold)
    boundaries_score = boundary_eval(segmentation,gold)
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