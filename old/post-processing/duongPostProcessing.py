import sys

import codecs

import glob

def read_file(path):
	return [line.strip("\n").split("\t") for line in codecs.open(path,"r","UTF-8")]




paths = glob.glob(sys.argv[1]+"*.txt")
outputPath = sys.argv[2]


for filem in paths:
	matrix = read_file(filem)
	for line in range(1,len(matrix)):
		for c in range(1,len(matrix[line])):
			#print matrix[line][c], matrix[line]
			if len(matrix[line]) == 2:
				pass
			elif c == 1:
				#print matrix[line][c], matrix
				matrix[line][c] = str((float(matrix[line][c]) + float(matrix[line][c+1]))/2)
			elif matrix[line][c] == matrix[line][-1]:
				matrix[line][c] = str((float(matrix[line][c]) + float(matrix[line][c-1]))/2)
			else:
				matrix[line][c] = str((float(matrix[line][c-1]) + float(matrix[line][c]) + float(matrix[line][c+1]))/3)
	with codecs.open(outputPath + filem.split("/")[-1],"w","UTF-8") as outputFile:
		for line in matrix:
			outputFile.write("\t".join(line) + "\n")
