# -*- coding: utf-8 -*-

import sys, codecs, glob, argparse
from entropy_gen import BaseMatrix
from utils import write_output_matrix, read_matrix_file

def get_merger_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument('-lang1','--lang1-matrices-folder', type=str, nargs='?', help='name of the matrix folder in each model folder')
	parser.add_argument('-lang2','--lang2-matrices-folder', type=str, nargs='?', help='name of the matrix folder in each model folder')
	parser.add_argument('-lang3','--lang3-matrices-folder', type=str, nargs='?', help='name of the matrix folder in each model folder')
	parser.add_argument('-lang4','--lang4-matrices-folder', type=str, nargs='?', help='name of the matrix folder in each model folder')
	parser.add_argument('--output-folder', type=str, nargs='?', help='folder for storing individual files')
	return parser

def write_log(log_list):
	counter = [0,0,0,0]
	for element in log_list:
		counter[element] +=1
	with open("log_count", "w") as output_log:
		for lang_count in counter:
			output_log.write(str(lang_count) + "\n")

def crop_matrix(matrix):
	if '</S>' in matrix[0]:
		for i in range(len(matrix)): #lines
			#print(matrix[i])
			del matrix[i][-1]

	if '<S>' in matrix[1]: #second line
		matrix.append(matrix[1])
		del matrix[1]
	return matrix

def get_entropy(matrix):
	entropies, _ = BaseMatrix.entropy(matrix)
	return sum(entropies) / (len(entropies)*1.0)

def get_min_entropy(matrices):
	min_e = get_entropy(matrices[0])
	index = 0
	min_matrix = matrices[0]
	for i in range(1, len(matrices)):
		this_e = get_entropy(matrices[i])
		if this_e < min_e:
			min_matrix = matrices[i]
			index = i
			min_e = this_e
	return min_matrix, index

def merger(args):
	print(args)
	lang1 = glob.glob(args.lang1_matrices_folder + "/*")
	lang2 = glob.glob(args.lang2_matrices_folder + "/*")
	#print(len(lang1), len(lang2))
	log = list()
	if args.lang3_matrices_folder:
		lang3 = glob.glob(args.lang3_matrices_folder + "/*")
	if args.lang4_matrices_folder:
		lang4 = glob.glob(args.lang4_matrices_folder + "/*")
	assert len(lang1) == len(lang2), "PROBLEM: Different number of files"
	for element in lang1:
		matrices = [read_matrix_file(element)]
		lang2_file = "/".join([args.lang2_matrices_folder, element.split("/")[-1]]) 
		matrices.append(read_matrix_file(lang2_file))
		if args.lang3_matrices_folder:
			lang3_file = "/".join([args.lang3_matrices_folder, element.split("/")[-1]]) 
			matrices.append(read_matrix_file(lang3_file))
		if args.lang4_matrices_folder:
			lang4_file = "/".join([args.lang4_matrices_folder, element.split("/")[-1]]) 
			matrices.append(read_matrix_file(lang4_file))
		for i in range(len(matrices)):
			matrices[i] = crop_matrix(matrices[i])
		
		try: 
			assert len(matrices[0]) == len(matrices[1]) #and len(matrices[0][0]) == len(matrices[1][0])
		except AssertionError:
			print("Matrices should have the same number of lines")
			exit(1)
		
		#print(len(matrices))
		
		min_matrix, index = get_min_entropy(matrices)
		log.append(index)
		output_path = "/".join([args.output_folder,  element.split("/")[-1]])
		write_output_matrix(output_path, min_matrix)
		write_log(log)


if __name__ == '__main__':
	parser = get_merger_parser()
	args = parser.parse_args()
	if len(sys.argv) < 3:
		parser.print_help()
		sys.exit(1)
	merger(args)
