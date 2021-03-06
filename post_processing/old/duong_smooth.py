# -*- coding: utf-8 -*-

import sys
import codecs
import glob

def read_file(path):
	return [line.strip("\n").split("\t") for line in codecs.open(path,"r","UTF-8")]

def write_output(matrix, path):
	with codecs.open(path,"w","UTF-8") as outputFile:
		for line in matrix:
			outputFile.write("\t".join(line) + "\n")


def smooth(paths, target, outputPath):
	for filem in paths:
		matrix = read_file(filem)
		if not target:
			matrix = [list(i) for i in zip(*matrix)]
		#s_matrix = [[0.0 for col in range(len(matrix[0]))] for row in range(len(matrix))]
		#s_matrix[0] = matrix[0]
		for line in range(1,len(matrix)):
			#s_matrix[line][0] = matrix[line][0]
			for column in range(1,len(matrix[line])):
				if len(matrix[line]) == 2:
					pass
				elif column == 1: #first line
					matrix[line][column] = str((float(matrix[line][column]) + float(matrix[line][column+1]))/2)
				elif matrix[line][column] == matrix[line][-1]: #last line
					matrix[line][column] = str((float(matrix[line][column]) + float(matrix[line][column-1]))/2)
				else:
					matrix[line][column] = str((float(matrix[line][column-1]) + float(matrix[line][column]) + float(matrix[line][column+1]))/3)
		write_output(matrix, outputPath + filem.split("/")[-1])

def main():
	if len(sys.argv) < 4:
		print("USAGE:\n\t[1] matrices folder\n\t[2] output folder\n\t[3] boolean, true for target\n")
		sys.exit(1)
	paths = glob.glob(sys.argv[1]+"*.txt")
	outputPath = sys.argv[2]
	target = bool(sys.argv[3])
	smooth(paths, target, outputPath)

if __name__ == '__main__':
	main()
