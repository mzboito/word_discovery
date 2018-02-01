# -*- coding: utf-8 -*-

import sys
import codecs
import glob
import numpy

def read_file(path):
	return [line.strip("\n").split("\t") for line in codecs.open(path,"r","UTF-8")]

def write_output(matrix, path):
	with codecs.open(path,"w","UTF-8") as outputFile:
		for line in matrix:
			outputFile.write("\t".join(line) + "\n")

def smooth(paths, reverse, outputPath):
	for filem in paths:
		matrix = read_file(filem)
		s_matrix = numpy.zeros(len(matrix), len(matrix[0]))
		for line in range(1,len(matrix)):
			for column in range(1,len(matrix[line])):
				if len(matrix[line]) == 2:
					pass
				elif column == 1: #first line
					s_matrix[line][column] = str((float(matrix[line][column]) + float(matrix[line][column+1]))/2)
				elif matrix[line][column] == matrix[line][-1]: #last line
					s_matrix[line][column] = str((float(matrix[line][column]) + float(matrix[line][column-1]))/2)
				else:
					s_matrix[line][column] = str((float(matrix[line][column-1]) + float(matrix[line][column]) + float(matrix[line][column+1]))/3)
		write_output(s_matrix, outputPath + filem.split("/")[-1])

def main():
	paths = glob.glob(sys.argv[1]+"*.txt")
	outputPath = sys.argv[2]
	reverse = bool(sys.argv[3])
	matrix = smooth(paths, reverse, outputPath)

if __name__ == '__main__':
	main()
