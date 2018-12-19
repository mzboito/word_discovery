# -*- coding: utf-8 -*-

import sys
import codecs
import glob
import argparse
import utils

def get_soft2hard_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--matrices-prefix', type=str, nargs='?', help='matrices prefix')
    parser.add_argument('--output-file', type=str, nargs='?', help='name for the output name')
    parser.add_argument('target',type=bool, default=False, nargs='?', help='default considers that the source is to segment, include this option to segment the target')
    parser.add_argument('--individual-files', type=str, nargs='?', help='list of names for generating individual files')
    parser.add_argument('--output-folder', type=str, nargs='?', help='folder for storing individual files')
    parser.add_argument('--translation', type=str, nargs='?', help='Creates a parallel file with the generated translation. It requires a suffix')
    parser.add_argument('--transformer', type=bool, default=False, nargs='?', help='set for transformer path getter')
    return parser

def get_path(number, paths, transformer):
    if transformer:
        for path in paths:
            if str(number) == path.split("/")[-1].split("_")[0]:
                return path
    else:
        for path in paths:
            if "." + str(number) + "." in path:
                return path
    #print(number)
    raise Exception("Path not found")

def get_max_prob_col(line, sentenceMatrix):
    maxValue = float(sentenceMatrix[line][1]) #start from the first line after the characters
    col = 1
    for i in range(2, len(sentenceMatrix[line])):
        if maxValue < float(sentenceMatrix[line][i]):
            col = i
            maxValue = float(sentenceMatrix[line][i])
    return col

def segment(filePath, target, translation):
    matrix = utils.read_matrix_file(filePath)
    if translation:
        return segment_target_translation(matrix, target)
    else:
        return segment_target(matrix, target),""

def segment_target(matrix, target):
    if not target:
        matrix = [list(i) for i in zip(*matrix)]
    finalString = ""
    lastCol = -1
    for i in range(1, len(matrix)): #for each element
        col = get_max_prob_col(i, matrix)
        if lastCol == -1: #first character
            finalString += matrix[i][0] #put the character in the beginning
        elif lastCol == col: # if the current character and the last one are not separated
            finalString += matrix[i][0]
        else:
            finalString += " " + matrix[i][0]
        lastCol = col
    finalString = finalString.replace("  "," ")
    if finalString[-1] == " ":
        finalString = finalString[:-1]
    if finalString[0] == " ":
        finalString = finalString[1:]
    return utils.clean_line(finalString)

def segment_target_translation(matrix, target):
    if not target:
        matrix = [list(i) for i in zip(*matrix)]
    finalString = ""
    translation = []
    lastCol = -1
    last_alignment = ""
    for i in range(1, len(matrix)): #for each element
        col = get_max_prob_col(i, matrix)
        aligned_word = matrix[0][col]
        if lastCol == -1: #first character
            finalString += matrix[i][0] #put the character in the beginning
            last_alignment = aligned_word
        elif lastCol == col: # if the current character and the last one are not separated
            finalString += matrix[i][0]
        else:
            finalString += " " + matrix[i][0]
            translation.append(last_alignment)
            last_alignment = aligned_word
        lastCol = col
    translation.append(last_alignment)
    finalString = finalString.replace("  "," ")
    if finalString[-1] == " ":
        finalString = finalString[:-1]
    if finalString[0] == " ":
        finalString = finalString[1:]
    discovered_words = finalString.split(" ")
    assert len(discovered_words) == len(translation)
    if discovered_words[-1] == utils.EOS_symbol: #if segmented the EOS symbol, we need to remove it and its aligned translation
        discovered_words = discovered_words[:-1]
        translation = translation[:-1]
    finalString = utils.clean_line(" ".join(discovered_words))
    return finalString, " ".join(translation)

def writeOutput(finalString, output, mode="w"):
    with codecs.open(output, mode, "UTF-8") as outputFile:
        outputFile.write(finalString + "\n")

def soft2hard(args):
    sentencesPaths = glob.glob(args.matrices_prefix+"*.txt") 
    if args.output_file: #segmentation on a single file
        outputPath = args.output_file
        for index in range(1, len(sentencesPaths)+1):
            filePath = get_path(index, sentencesPaths, args.transformer)
            finalstr, translation = segment(filePath, args.target, args.translation)
            writeOutput(finalstr, outputPath, "a")
            if args.translation:
                writeOutput(translation, outputPath+args.translation,"a")

    if args.individual_files and args.output_folder: #segmentation in individual files (with ID)
        files_output_list = utils.read_file(args.individual_files)
        folder = args.output_folder if args.output_folder[-1] == '/' else args.output_folder + '/'
        assert len(files_output_list) == len(sentencesPaths)
        for index in range(1, len(sentencesPaths)+1):
            filePath = get_path(index, sentencesPaths, args.transformer)
            finalstr, translation = segment(filePath, args.target, args.translation)
            file_name = files_output_list[index-1].split("/")[-1] + ".hs" #split(".")[:-1]) + ".hardseg"
            writeOutput(finalstr, folder + file_name)
            if args.translation:
                writeOutput(translation, folder + file_name +args.translation)

    elif args.output_folder: #segmentation in individual files (without ID)
        folder = args.output_folder if args.output_folder[-1] == '/' else args.output_folder + '/'
        for sentencePath in sentencesPaths:
            finalstr, translation = segment(sentencePath, args.target, args.translation)
            file_name = sentencePath.split("/")[-1] + ".hs" #split(".")[:-1]) + ".hardseg"
            writeOutput(finalstr, folder + file_name)
            if args.translation:
                writeOutput(translation, folder + file_name +args.translation)


if __name__ == "__main__":
    parser = get_soft2hard_parser()
    args = parser.parse_args()
    if len(sys.argv) < 3 or not args.matrices_prefix:
        parser.print_help()
        sys.exit(1)
    soft2hard(args)
