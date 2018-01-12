# -*- coding: utf-8 -*-

import sys
import codecs

def get_score(gold, unsup):
    words = gold.split(" ")
    expWords = unsup.split(" ")
    score = 0
    for word in expWords:
        if word in words:
            words.remove(word) #avoid multiples matches for incorrect substrings
            score += 1
    return score

def print_usage():
    print "PRF evaluation\n"
    print "arg1: generated segmentation\narg2: gold segmentation\narg3: output file\n"

def readFile(inputPath):
    return [line.strip("\n") for line in codecs.open(inputPath, "r", "UTF-8")]

def evaluate(generated_seg, gold_seg):
    tokens = evaluate_tokens(generated_seg, gold_seg)
    types = evaluate_types(generated_seg, gold_seg)
    return [tokens, types]

def recall(numberCorrect, totalNumberGold):
    return float(numberCorrect) / totalNumberGold

def precision(numberCorrect, totalNumberUnsup):
    return float(numberCorrect) / totalNumberUnsup

def fscore(r, p):
    return 2.0*r*p / (p + r)

def evaluate_tokens(generated_seg, gold_seg):
    numberTokensGold =0
    numberTokensUnsup =0
    numberCorrectTokens =0
    for i in range(0, len(gold_seg)):
        line_tokens = len(gold_seg[i].split(" ")) #number of tokens in that line
        line_generated = len(generated_seg[i].split(" ")) #same
        correctly_segmented = get_score(gold_seg[i], generated_seg[i]) #number of tokens found
        numberTokensGold += line_tokens
        numberTokensUnsup += line_generated
        numberCorrectTokens += correctly_segmented
    p = precision(numberCorrectTokens, numberTokensUnsup)
    r = recall(numberCorrectTokens, numberTokensGold)
    return [p, r, fscore(r, p)]

def get_types(sentencesList):
    types = []
    for i in range(0, len(sentencesList)):
        for word in sentencesList[i].split(" "):
            if not word in types:
                types.append(word)
    return types

def filter_types(gold, words):
    newWords = []
    for word in words:
        if word in gold:
            newWords.append(word)
    return newWords

def evaluate_types(generated_seg, gold_seg):
    types_gold = get_types(gold_seg)
    types_unsup = get_types(generated_seg)
    correct_types = filter_types(types_gold, types_unsup)


    numberTypesGold = len(types_gold)
    numberTypesUnsup = len(types_unsup)
    numberCorrectTypes = len(correct_types)

    r = recall(numberCorrectTypes, numberTypesGold)
    p = precision(numberCorrectTypes, numberTypesUnsup)

    return [p, r, fscore(r,p)]


def write_output(metrics, output_name):
    with open(output_name,"w") as output_file:
        output_file.write("\tPRECISION\tRECALL\tF-SCORE\n")
        output_file.write("\t".join("TYPES", str(metrics[1][0]), str(metrics[1][1]), str(metrics[1][2]))+"\n")
        output_file.write("\t".join("TOKENS", str(metrics[0][0]), str(metrics[0][1]), str(metrics[0][2]))+"\n")

def main():
    if len(sys.argv) == 4:
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
