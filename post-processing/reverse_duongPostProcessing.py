import sys

import codecs

import glob

def read_file(path):
	return [line.strip("\n").split("\t") for line in codecs.open(path,"r","UTF-8")]




paths = glob.glob(sys.argv[1]+"*.txt")
outputPath = sys.argv[2]


for filem in paths:
	matrix = read_file(filem)
	for c in range(1,len(matrix[0])):
		for line in range(1, len(matrix)):
			if len(matrix) == 2: 
				pass
			elif line == 1:
				matrix[line][c] = str((float(matrix[line][c]) + float(matrix[line+1][c]))/2)
			elif matrix[line][c] == matrix[-1][c]:
				matrix[line][c] = str((float(matrix[line][c]) + float(matrix[line-1][c]))/2)
			else:
				matrix[line][c] = str((float(matrix[line-1][c]) + float(matrix[line][c]) + float(matrix[line+1][c]))/3)
	with codecs.open(outputPath + filem.split("/")[-1],"w","UTF-8") as outputFile:
		for line in matrix:		
			outputFile.write("\t".join(line) + "\n")














