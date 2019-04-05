# -*- coding: utf-8 -*-

import sys
import codecs
import glob
import argparse
import utils
from Entropy import entropy, format_distribution

def get_soft2hard_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--matrices-prefix', type=str, nargs='?', help='matrices prefix')
    parser.add_argument('--output-file', type=str, nargs='?', help='name for the output name')
    #This target option is fixed because I do not experiment in the other direction anymore
    parser.add_argument('target',type=bool, default=True, nargs='?', help='default considers that the source is to segment, include this option to segment the target')
    parser.add_argument('--individual-files', type=str, nargs='?', help='list of names for generating individual files')
    parser.add_argument('--output-folder', type=str, nargs='?', help='folder for storing individual files')
    parser.add_argument('--translation', default=False, action='store_true', help='Creates a parallel file with the generated translation. It requires a suffix')
    #merge this two parameters in the future
    parser.add_argument('--transformer', default=False, action='store_true', help='set for transformer path getter')
    parser.add_argument('--pervasive', default=False, action='store_true', help='set for pervasive path getter')
    parser.add_argument('--type-entropy', default=False, action='store_true', help='computes the average entropy for each discovered type')
    return parser

def get_path(number, paths, transformer=False, pervasive=False):
    if transformer or pervasive:
        token = "_" if transformer else "."
        for path in paths:
            if str(number) == path.split("/")[-1].split(token)[0]: 
                return path
    else:
        for path in paths:
            if "." + str(number) + "." in path:
                return path
    raise Exception("Path not found")

def get_max_prob_col(line, sentenceMatrix):
    col = 1
    maxValue = float(sentenceMatrix[line][col]) #start from the first line after the characters
    for i in range(2, len(sentenceMatrix[line])):
        if maxValue < float(sentenceMatrix[line][i]):
            col = i
            maxValue = float(sentenceMatrix[line][i])
    return col

def segment(file_path, target, translation):
    matrix = utils.read_matrix_file(file_path)
    if translation:
        return segment_target_translation(matrix, target)
    else:
        return segment_target(matrix, target), ""

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

def write_output(finalString, output, mode="w"):
    with codecs.open(output, mode, "UTF-8") as outputFile:
        outputFile.write(finalString + "\n")

def types_entropy(f_path, dictionary):
    matrix = utils.read_matrix_file(f_path)
    index_list = []
    discovered_tokens = [""]
    last_col = -1
    for i in range(1, len(matrix)): #for each line
        col = get_max_prob_col(i, matrix) #find its alignment
        if last_col == -1: #first element
            index_list.append([i])
            discovered_tokens[-1] += matrix[i][0] #put the character in the beginning
        elif last_col == col: # if the current character and the last one are not separated
            discovered_tokens[-1] += matrix[i][0]
            index_list[-1].append(i)
        else:
            discovered_tokens.append(matrix[i][0])
            index_list.append([i])
        last_col = col
    for i in range(len(discovered_tokens)):
        token = discovered_tokens[i].replace("</S>","")
        if len(token) > 0:
            avg_entropy = 0.0
            if token not in dictionary:
                dictionary[token] = list()
            for index in index_list[i]:
                #print(matrix[index])
                avg_entropy += entropy(format_distribution(matrix[index])) #matrix[index], 
            avg_entropy /= len(index_list[i])
            dictionary[token].append((avg_entropy, f_path.split("/")[-1]))
    return dictionary

def write_dictionary(f_path, dictionary):
    with open(f_path, "w") as output_file:
        for token in dictionary.keys():
            average = sum([info[0] for info in dictionary[token]]) / len(dictionary[token])
            output_file.write("\t".join([token, str(average)]) + "\n")
            #for entropy, f_id in dictionary[token]:
            #output_file.write("\t".join([token, str(entropy), f_id]) + "\n")

def run(args):
    sentencesPaths = glob.glob(args.matrices_prefix+"*.txt") 

    if args.type_entropy:
        output_path = args.output_file
        TYPES = dict()
        for index in range(1, len(sentencesPaths)+1):
            # get file
            '''try:
                file_path = get_path(index, sentencesPaths, transformer=args.transformer, pervasive=args.pervasive)
            except Exception:
                '''
            file_path = sentencesPaths[index-1]
            #get dictionary, token
            TYPES = types_entropy(file_path, TYPES)
        write_dictionary(output_path, TYPES)


    elif args.output_file: #segmentation on a single file
        output_path = args.output_file
        for index in range(1, len(sentencesPaths)+1):
            file_path = get_path(index, sentencesPaths, transformer=args.transformer, pervasive=args.pervasive)
            finalstr, translation = segment(file_path, args.target, args.translation)
            write_output(finalstr, output_path, "a")
            if args.translation:
                write_output(translation, output_path+args.translation,"a")

    if args.individual_files and args.output_folder: #segmentation in individual files (with ID)
        files_output_list = utils.read_file(args.individual_files)
        folder = args.output_folder if args.output_folder[-1] == '/' else args.output_folder + '/'
        assert len(files_output_list) == len(sentencesPaths)
        for index in range(1, len(sentencesPaths)+1):
            file_path = get_path(index, sentencesPaths, transformer=args.transformer, pervasive=args.pervasive)
            finalstr, translation = segment(file_path, args.target, args.translation)
            file_name = files_output_list[index-1].split("/")[-1] + ".hs" #split(".")[:-1]) + ".hardseg"
            write_output(finalstr, folder + file_name)
            if args.translation:
                write_output(translation, folder + file_name +args.translation)

    elif args.output_folder: #segmentation in individual files (without ID)
        folder = args.output_folder if args.output_folder[-1] == '/' else args.output_folder + '/'
        for sentencePath in sentencesPaths:
            finalstr, translation = segment(sentencePath, args.target, args.translation)
            file_name = sentencePath.split("/")[-1] + ".hs" #split(".")[:-1]) + ".hardseg"
            write_output(finalstr, folder + file_name)
            if args.translation:
                write_output(translation, folder + file_name +args.translation)


if __name__ == "__main__":
    parser = get_soft2hard_parser()
    args = parser.parse_args()
    if len(sys.argv) < 3 or not args.matrices_prefix:
        parser.print_help()
        sys.exit(1)
    run(args)
