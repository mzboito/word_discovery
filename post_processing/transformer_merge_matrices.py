# -*- coding: utf-8 -*-

import sys, codecs, glob
import argparse
from utils import transformer_decoder, generate_heads, read_matrix_file, write_output_matrix
from merge_matrices import merge_matrices

def get_folders(root_dir, layers):
    return [["/".join([root_dir, key, str(layer), attention]) for layer in range(1,int(args.layers)+1) for attention in transformer_decoder[key]] for key in transformer_decoder.keys()][0]

def get_file_names(folder, heads):  
    paths = glob.glob(folder + "/*")
    if heads == '1':
        return [path.split("/")[-1] for path in paths if "avg" not in path]
    return [path.split("/")[-1] for path in paths]

def get_matrices(folders, f_name):
    matrices = []
    for folder in folders:
        matrices.append(read_matrix_file(folder + "/" + f_name))
    return matrices

def merger(args):
    folders = get_folders(args.root_folder, args.layers)
    f_names = get_file_names(folders[0], args.heads)
    #print(f_names)
    for f_name in f_names:
        matrices = get_matrices(folders, f_name)
        average_matrix = merge_matrices(matrices)
        write_output_matrix(args.output_folder + "/" + f_name, average_matrix)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--root-folder', type=str, nargs='?', help='root directory for the attention folders')
    parser.add_argument('--heads', type=str, nargs='?', help='number of heads')
    parser.add_argument('--layers', type=str, nargs='?', help='number of layers')
    parser.add_argument('--output-folder', type=str, nargs='?', help='root directory for the attention folders')
    args = parser.parse_args()
    if not (args.root_folder and args.output_folder and args.layers and args.heads):
        parser.print_help()
        sys.exit(1)
    merger(args)
