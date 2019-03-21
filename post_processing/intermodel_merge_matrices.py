# -*- coding: utf-8 -*-

import sys, codecs, glob, argparse
from utils import write_output_matrix, read_matrix_file

def get_merger_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument('--lang1-matrices-folder', type=str, nargs='?', help='name of the matrix folder in each model folder')
	parser.add_argument('--lang2-matrices-folder', type=str, nargs='?', help='name of the matrix folder in each model folder')
	parser.add_argument('--output-folder', type=str, nargs='?', help='folder for storing individual files')
	parser.add_argument('--model-prefix', type=str, default="run", nargs='?', help='prefix name for the models folders')
	return parser

def merge_matrices(matrices_list):
	num_lines = len(matrices_list[0])
	num_columns = len(matrices_list[0][0]) 
	num_matrices = len(matrices_list)
	output = [[0 for i in range(num_columns)] for j in range(num_lines)]
	output[0] = matrices_list[0][0]
	for line in range(1, num_lines):
		output[line][0] = matrices_list[0][line][0]
		for column in range(1, num_columns):
			for i in range(0, num_matrices):
				if len(matrices_list[i][line]) > 1:
					output[line][column] += float(matrices_list[i][line][column])
			output[line][column] = str(output[line][column] / num_matrices)
	return output

def crop_matrix(matrix):
	#print('</S>' in matrix[0])
	#print('<S>' in matrix[1])
	if '</S>' in matrix[0]:
		for i in range(len(matrix)): #lines
			#print(matrix[i])
			del matrix[i][-1]

	if '<S>' in matrix[1]: #second line
		matrix.append(matrix[1])
		#print(matrix)
		del matrix[1]
		#matrix.append(line)
		#print(matrix)

	return matrix

def merger(args):
	print(args)
	lang1 = glob.glob(args.lang1_matrices_folder + "/*")
	lang2 = glob.glob(args.lang2_matrices_folder + "/*")
	assert len(lang1) == len(lang2), "PROBLEM: Different number of files"
	for element in lang1:
		matrices = [read_matrix_file(element)]
		lang2_file = "/".join([args.lang2_matrices_folder, element.split("/")[-1]]) 
		matrices.append(read_matrix_file(lang2_file))

		crop_matrix(matrices[0])
		crop_matrix(matrices[1])

		
		try: 
			assert len(matrices[0]) == len(matrices[1]) and len(matrices[0][0]) == len(matrices[1][0]), "Matrices should have the same dimension"
		except AssertionError:
			'''for element in matrices[0]:
				print(element[0])
			print()
			for element in matrices[1]:
				print(element[0])'''

			'''print()
			print(len(matrices[0]),len(matrices[0][0]))
			print(len(matrices[1]), len(matrices[1][0]))
			print(element.split("/")[-1])'''
			temp = matrices[1][:101]
			temp.append(matrices[1][-1])
			matrices[1] = temp
			print(len(matrices[0]),len(matrices[0][0]))
			print(len(matrices[1]), len(matrices[1][0]))
			#print(temp)
			#exit(1)
		avg_matrix = merge_matrices(matrices)
		output_path = "/".join([args.output_folder,  element.split("/")[-1]])
		write_output_matrix(output_path, avg_matrix)


if __name__ == '__main__':
	parser = get_merger_parser()
	args = parser.parse_args()
	if len(sys.argv) < 4:
		parser.print_help()
		sys.exit(1)
	merger(args)
