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
    parser.add_argument('--output-folder', type=str, nargs='?', help='folder for storing individual files')
    parser.add_argument('--individual-files', type=str, nargs='?', help='list of names for generating individual files')
    # This target option is fixed because I do not experiment in the other direction anymore
    parser.add_argument('target',type=bool, default=True, nargs='?', help='default considers that the source is to segment, include this option to segment the target')
    # This changes the ids
    parser.add_argument('--translation', default=False, action='store_true', help='Creates a parallel file with the generated translation. It requires a suffix')
    parser.add_argument('--transformer', default=False, action='store_true', help='set for transformer path getter')
    parser.add_argument('--pervasive', default=False, action='store_true', help='set for pervasive path getter')
    # entropy stuff
    parser.add_argument('--type-entropy', default=False, action='store_true', help='computes the average entropy for each discovered type')
    parser.add_argument('--translation-entropy', default=False, action='store_true', help='computes the average entropy for each (type, translation) pair')
    parser.add_argument('--ngram-entropy', type=int, nargs='?', help='computes the average entropy for discovered ngram in the corpus')
    # TO IMPLEMENT
    parser.add_argument('--entropy-study', default=False, action='store_true', help='generates token, translation and ngram entropy on a single table (sorted by text_id)')
    return parser


def get_max_prob_col(line, sentenceMatrix):
    col = 1
    maxValue = float(sentenceMatrix[line][col]) #start from the first line after the characters
    for i in range(2, len(sentenceMatrix[line])):
        this_col = float(sentenceMatrix[line][i])
        if maxValue < this_col:
            maxValue = this_col
            col = i
    return col

def segment(file_path, target=True):
    matrix = utils.read_matrix_file(file_path)
    return segment_target(matrix, target)

def segment_target(matrix, target):
    discovered_words, index_list, discovered_translation = get_distributions(matrix, target)
    assert len(discovered_words) == len(discovered_translation)
    if discovered_words[-1] == utils.EOS_symbol: #if segmented the EOS symbol, we need to remove it and its aligned translation
        discovered_words = discovered_words[:-1]
        discovered_translation = discovered_translation[:-1]
    sentence = utils.clean_line(" ".join(discovered_words))
    return sentence, " ".join(discovered_translation)

def get_distributions(matrix, target=True):
    if not target:
        matrix = [list(i) for i in zip(*matrix)]
    index_list = []
    discovered_tokens = [""]
    discovered_translation = []
    last_alignment = ""
    last_col = -1
    for i in range(1, len(matrix)): #for each line
        col = get_max_prob_col(i, matrix) #find its alignment
        aligned_word = matrix[0][col]
        if last_col == -1: #first element
            index_list.append([i])
            discovered_tokens[-1] += matrix[i][0] #put the character in the beginning
            last_alignment = aligned_word
        elif last_col == col: # if the current character and the last one are not separated
            discovered_tokens[-1] += matrix[i][0]
            index_list[-1].append(i)
        else:
            discovered_tokens.append(matrix[i][0])
            discovered_translation.append(last_alignment)
            last_alignment = aligned_word
            index_list.append([i])
        last_col = col
    discovered_translation.append(last_alignment)
    discovered_tokens[-1] = discovered_tokens[-1].replace("</S>","")
    return discovered_tokens, index_list, discovered_translation

def get_matrix_entropy(f_path, dictionary, str_id=None):
    matrix = utils.read_matrix_file(f_path)
    discovered_tokens, index_list, discovered_translation = get_distributions(matrix)
    key = f_path.split("/")[-1] if not str_id else str_id #uses individual id if available
    #.split(".")[0]
    dictionary[key] = list()
    for i in range(len(discovered_tokens)):
        token = discovered_tokens[i].replace("</S>","").replace("#","")
        translation = discovered_translation[i]
        if len(token) > 0:
            avg_entropy = get_average_entropy(matrix, index_list[i])
            dictionary[key] += [(token, translation, avg_entropy)]
    return dictionary

def get_average_entropy(matrix, index_list):
    return sum([entropy(format_distribution(matrix[index])) for index in index_list]) / len(index_list)

def generate_types_dictionary(dictionary):
    types_dict = dict()
    for key in dictionary.keys():
        for token, translation, entropy in dictionary[key]:
            if token not in types_dict:
                types_dict[token] = [[],[]]
            types_dict[token][0].append(entropy) #saves token ane
            types_dict[token][1].append(key) #saves ids

    for element in types_dict.keys():
        avg_entropy = sum(value for value in types_dict[element][0]) / len(types_dict[element][0])
        types_dict[element] = [avg_entropy, ";".join(types_dict[element][1])]
    print(len(types_dict.keys()))
    return types_dict

def generate_translation_dictionary(dictionary):
    print("generating translation dictionary")
    translation_dict = dict()
    types = list()
    for key in dictionary.keys():
        for token, translation, entropy in dictionary[key]:
            if token not in types:
                types.append(token)
            entry = "##".join([token, translation])
            if entry not in translation_dict:
                translation_dict[entry] = [[],[]]
            translation_dict[entry][0].append(entropy)
            translation_dict[entry][1].append(key)
    teste = list()
    for element in translation_dict.keys():
        teste.append(element.split("##")[0])
        avg_entropy = sum(value for value in translation_dict[element][0]) / len(translation_dict[element][0])
        translation_dict[element] = [avg_entropy, ";".join(translation_dict[element][1])]
    print(len(types))
    print(len(translation_dict.keys()))
    print(len(set(teste)))
    return translation_dict

'''def translation_entropy(f_path, dictionary):
    matrix = utils.read_matrix_file(f_path)
    discovered_tokens, index_list, discovered_translation = get_distributions(matrix)
    for i in range(len(discovered_tokens)):
        token = discovered_tokens[i].replace("</S>","")
        translation = discovered_translation[i]
        key = "_".join([token, translation])
        if len(token) > 0:
            if key not in dictionary:
                dictionary[key] = list()
            avg_entropy = get_average_entropy(matrix, index_list[i])
            dictionary[key].append((avg_entropy, f_path.split("/")[-1]))
    return dictionary
'''
'''def types_entropy(f_path, dictionary):
    matrix = utils.read_matrix_file(f_path)
    discovered_tokens, index_list, _ = get_distributions(matrix)
    for i in range(len(discovered_tokens)):
        token = discovered_tokens[i].replace("</S>","")
        if len(token) > 0:
            if token not in dictionary:
                dictionary[token] = list()
            avg_entropy = get_average_entropy(matrix, index_list[i])
            dictionary[token].append((avg_entropy, f_path.split("/")[-1]))
    return dictionary'''


def generate_ngrams(dictionary, N):
    tokens = list(dictionary.keys()) #/!\ will not work correctly with python version < 3.6 (sorted dictionary)
    return list(zip(*[tokens[i:] for i in range(N)]))

def ngrams_entropy(f_path, dictionary, N=2):
    temp_dict = get_matrix_entropy(f_path, dict())
    temp_dict = generate_types_dictionary(temp_dict)
    sets = generate_ngrams(temp_dict, N)
    for ngram in sets:
        avg_entropy = 0.0
        for element in ngram:
            avg_entropy += temp_dict[element][0][0]
        avg_entropy /= N
        key = "_".join(list(ngram))
        if key not in dictionary:
            dictionary[key] = [(avg_entropy,f_path.split("/")[-1])]
        else:
            dictionary[key].append((avg_entropy,f_path.split("/")[-1]))
    return dictionary

def run(args):
    sentencesPaths = glob.glob(args.matrices_prefix+"*.txt") 

    if args.entropy_study or args.type_entropy or args.translation_entropy:
        output_path = args.output_file
        CORPUS = dict()
        if args.individual_files:
            files_output_list = utils.read_file(args.individual_files)
            assert len(files_output_list) == len(sentencesPaths)
        for index in range(1, len(sentencesPaths)+1):
            file_path = sentencesPaths[index-1]
            file_name = files_output_list[index-1].split("/")[-1] if args.individual_files else None
            CORPUS = get_matrix_entropy(file_path, CORPUS, str_id=file_name)
        if args.type_entropy:
            CORPUS = generate_types_dictionary(CORPUS)
        elif args.translation_entropy:
            CORPUS = generate_translation_dictionary(CORPUS)
        utils.write_dictionary(output_path, CORPUS)
        '''#TO DO FIX ME
        elif args.type_entropy:
            output_path = args.output_file
            CORPUS = dict()
            for index in range(1, len(sentencesPaths)+1):
                file_path = sentencesPaths[index-1]
                CORPUS = get_matrix_entropy(file_path, CORPUS)
            utils.write_dictionary(output_path, TYPES)
        #TO DO FIX ME
        elif args.translation_entropy:
            output_path = args.output_file
            ALIGNED = dict()
            for index in range(1, len(sentencesPaths)+1):
                file_path = sentencesPaths[index-1]
                ALIGNED = translation_entropy(file_path, ALIGNED)
            utils.write_dictionary(output_path, ALIGNED)''' 
    #TO DO FIX ME
    elif args.ngram_entropy:
        output_path = args.output_file
        NGRAMS = dict()
        for index in range(1, len(sentencesPaths)+1):
            file_path = sentencesPaths[index-1]
            NGRAMS = ngrams_entropy(file_path, NGRAMS, args.ngram_entropy)
        utils.write_dictionary(output_path, NGRAMS)

    elif args.output_file: #segmentation on a single file
        output_path = args.output_file
        for index in range(1, len(sentencesPaths)+1):
            file_path = utils.get_path(index, sentencesPaths, transformer=args.transformer, pervasive=args.pervasive)
            finalstr, translation = segment(file_path, args.target)
            utils.write_output(finalstr, output_path, "a")
            if args.translation:
                utils.write_output(translation, output_path+args.translation,"a")

    if args.individual_files and args.output_folder: #segmentation in individual files (with ID)
        files_output_list = utils.read_file(args.individual_files)
        folder = args.output_folder if args.output_folder[-1] == '/' else args.output_folder + '/'
        assert len(files_output_list) == len(sentencesPaths)
        for index in range(1, len(sentencesPaths)+1):
            file_path = utils.get_path(index, sentencesPaths, transformer=args.transformer, pervasive=args.pervasive)
            finalstr, translation = segment(file_path, args.target)
            file_name = files_output_list[index-1].split("/")[-1] + ".hs" #split(".")[:-1]) + ".hardseg"
            utils.write_output(finalstr, folder + file_name)
            if args.translation:
                utils.write_output(translation, folder + file_name +args.translation)

    elif args.output_folder: #segmentation in individual files (without ID)
        folder = args.output_folder if args.output_folder[-1] == '/' else args.output_folder + '/'
        for sentencePath in sentencesPaths:
            finalstr, translation = segment(sentencePath, args.target)
            file_name = sentencePath.split("/")[-1] + ".hs" #split(".")[:-1]) + ".hardseg"
            utils.write_output(finalstr, folder + file_name)
            if args.translation:
                utils.write_output(translation, folder + file_name +args.translation)

if __name__ == "__main__":
    parser = get_soft2hard_parser()
    args = parser.parse_args()
    if len(sys.argv) < 3 or not args.matrices_prefix:
        parser.print_help()
        sys.exit(1)
    run(args)
