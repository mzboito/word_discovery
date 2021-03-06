# -*- coding: utf-8 -*-

import sys
import codecs
import glob
import argparse
import utils
from Entropy import entropy, format_distribution

def get_max_prob_col(line, sentenceMatrix):
    col = 1
    maxValue = float(sentenceMatrix[line][col]) #start from the first line after the characters
    for i in range(2, len(sentenceMatrix[line])):
        this_col = float(sentenceMatrix[line][i])
        if maxValue < this_col:
            maxValue = this_col
            col = i
    return col

def cat_tokens(discovered_tokens):
    return ["".join(token) for token in discovered_tokens]

def get_distributions(matrix, target=True, lab_lst=None,eos=True):
    if not target:
        matrix = [list(i) for i in zip(*matrix)]
    tgt_index = []
    src_index = []
    discovered_tokens = [[]]
    discovered_translation = []
    last_alignment = ""
    last_col = -1
    index_labs = 0
    for i in range(1, len(matrix)): #for each line
        col = get_max_prob_col(i, matrix) #find its alignment
        aligned_word = matrix[0][col]
        silence_flag = lab_lst and lab_lst[index_labs][0] == utils.SIL_symbol
        if silence_flag and i +1 < len(matrix):
            while index_labs < len(lab_lst) and lab_lst[index_labs][0] == utils.SIL_symbol:
                index_labs +=1
        if lab_lst:
            assert (i+1) == len(matrix) or lab_lst[index_labs][0] == matrix[i][0]
        if last_col == -1: #first element
            tgt_index.append([i-1])
            discovered_tokens[-1].append(matrix[i][0]) #put the character in the beginning
            last_alignment = aligned_word
        elif last_col == col and not silence_flag: # if the current character and the last one are not separated
            discovered_tokens[-1].append(matrix[i][0])
            tgt_index[-1].append(i-1)
        else:
            discovered_tokens.append([matrix[i][0]])
            discovered_translation.append(last_alignment)
            src_index.append(last_col-1)
            last_alignment = aligned_word
            tgt_index.append([i-1])
        index_labs +=1
        last_col = col
    src_index.append(last_col)
    discovered_translation.append(last_alignment)
    if eos:
        discovered_tokens[-1] = ["".join(discovered_tokens[-1]).replace(utils.EOS_symbol,"")] #("</S>","")
    return discovered_tokens, discovered_translation, tgt_index, src_index

def get_matrix_entropy(f_path, dictionary, lab_lst=None, str_id=None, dispersion=False):
    matrix = utils.read_matrix_file(f_path)
    discovered_tokens, discovered_translation, tgt_index, src_index = get_distributions(matrix, lab_lst=lab_lst)
    discovered_tokens = cat_tokens(discovered_tokens)
    key = f_path.split("/")[-1] if not str_id else str_id #uses individual id if available
    dictionary[key] = list()
    for i in range(len(discovered_tokens)):
        token = discovered_tokens[i].replace(utils.EOS_symbol,"").replace("#","")
        translation = discovered_translation[i]
        if len(token) > 0:
            avg_entropy = get_average_entropy(matrix, tgt_index[i])
            dictionary[key] += [(token, translation, avg_entropy)]
    if not dispersion:
        return dictionary
    else:
        dispersion[key] = (len(set(discovered_tokens)) * 1.0) / (len(matrix[0][0])-1)
        return dictionary, dispersion

def get_average_entropy(matrix, tgt_index):
    return sum([entropy(format_distribution(matrix[index+1])) for index in tgt_index]) / len(tgt_index)




