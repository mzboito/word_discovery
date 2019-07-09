# -*- coding: utf-8 -*-

import sys
import codecs
import glob
import argparse
import utils 
import soft2hard as s2h
from Entropy import entropy, format_distribution

def get_soft2hard_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--matrices-prefix', type=str, nargs='?', help='matrices prefix')
    parser.add_argument('--output-file', type=str, nargs='?', help='name for the output name')
    parser.add_argument('--output-folder', type=str, nargs='?', help='folder for storing individual files')
    parser.add_argument('--individual-files', type=str, nargs='?', help='list of names for generating individual files')
    parser.add_argument('--silence', type=str, nargs='?', help='folder containing the silence indexes')
    # This target option is fixed because I do not experiment in the other direction anymore
    parser.add_argument('target',type=bool, default=True, nargs='?', help='default considers that the source is to segment, include this option to segment the target')
    # This changes the ids
    parser.add_argument('--translation', default=False, action='store_true', help='Creates a parallel file with the generated translation. It requires a suffix')
    parser.add_argument('--transformer', default=False, action='store_true', help='set for transformer path getter')
    parser.add_argument('--pervasive', default=False, action='store_true', help='set for pervasive path getter')
    return parser

def segment(file_path, target=True, silence=None):
    matrix = utils.read_matrix_file(file_path)
    return segment_target(matrix, target, silence=silence)

def segment_target(matrix, target, silence=None):
    discovered_words, index_list, discovered_translation = s2h.get_distributions(matrix, target, lab_lst=silence)
    assert len(discovered_words) == len(discovered_translation)
    if discovered_words[-1] == utils.EOS_symbol: #if segmented the EOS symbol, we need to remove it and its aligned translation
        discovered_words = discovered_words[:-1]
        discovered_translation = discovered_translation[:-1]
    sentence = utils.clean_line(" ".join(discovered_words))
    return sentence, " ".join(discovered_translation)


def run(args):
    sentencesPaths = glob.glob(args.matrices_prefix+"*.txt") 
    if args.output_file: #segmentation on a single file
        output_path = args.output_file
        for index in range(1, len(sentencesPaths)+1):
            file_path = utils.get_path(index, sentencesPaths, transformer=args.transformer, pervasive=args.pervasive)
            finalstr, translation = segment(file_path, target=args.target)
            utils.write_output(finalstr, output_path, "a")
            if args.translation:
                utils.write_output(translation, output_path+args.translation,"a")

    if args.individual_files and args.output_folder: #segmentation in individual files (with ID)
        files_output_list = utils.read_file(args.individual_files)
        folder = args.output_folder if args.output_folder[-1] == '/' else args.output_folder + '/'
        silence_dict = utils.read_lab_files(args.silence) if args.silence else None
        assert len(files_output_list) == len(sentencesPaths)
        for index in range(1, len(sentencesPaths)+1):
            file_path = utils.get_path(index, sentencesPaths, transformer=args.transformer, pervasive=args.pervasive)
            sentence_id = files_output_list[index-1].split("/")[-1]
            file_name = sentence_id + ".hs" 
            sil_list = silence_dict[sentence_id] if args.silence else None
            finalstr, translation = segment(file_path, target=args.target, silence=sil_list)
            utils.write_output(finalstr, folder + file_name)
            if args.translation:
                utils.write_output(translation, folder + file_name +args.translation)

    elif args.output_folder: #segmentation in individual files (without ID)
        folder = args.output_folder if args.output_folder[-1] == '/' else args.output_folder + '/'
        silence_dict = utils.read_lab_files(args.silence) if args.silence else None
        for sentencePath in sentencesPaths:
            sentence_id = ".".join(sentencePath.split("/")[-1].split(".")[:-1])
            #print(silence_dict)
            sil_list = silence_dict[sentence_id] if args.silence else None
            finalstr, translation = segment(sentencePath, target=args.target, silence=sil_list)
            file_name = sentencePath.split("/")[-1] + ".hs"
            utils.write_output(finalstr, folder + file_name)
            if args.translation:
                utils.write_output(translation, folder + file_name +args.translation)

if __name__ == "__main__":
    parser = get_soft2hard_parser()
    args = parser.parse_args()
    if len(sys.argv) < 3 or not args.matrices_prefix:
        parser.print_help()
        sys.exit(1)
    '''if args.silence and not args.individual_files:
        raise Exception("SILENCE OPTION ONLY WORKS WITH INDIVIDUAL-FILES PARAMETER!")'''
    run(args)
