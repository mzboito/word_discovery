import argparse, sys, glob

import soft2hard, utils
from praatio import tgio

def extract(args):
    f_names = glob.glob(args.input_folder+"/*.txt")
    for f_name in f_names:
        print(f_name)
        matrix = utils.read_matrix_file(f_name)
        print("\t".join(matrix[0]))
        a = soft2hard.get_distributions(matrix,target=False)
        print(a)
        exit(1)
        # read matrix
        #generate alignment
        #figure out how to put it on a textgrid



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-folder', type=str, nargs='?', help='folder containing the attention matrices')
    args = parser.parse_args()
    extract(args)