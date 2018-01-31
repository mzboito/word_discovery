# -*- coding: utf-8 -*-

import sys
import codecs
import glob
import argparse

def getPath(number, paths):
    for path in paths:
        if "." + str(number) + "." in path:
            return path
    return None

def readMatrixFile(path):
    return [line.strip("\n").split("\t") for line in codecs.open(path,"r","UTF-8")]

def getMaxProbCol(line, sentenceMatrix):
    maxValue = float(sentenceMatrix[line][1]) #start from the first line after the characters
    col = 1
    for i in range(2, len(sentenceMatrix[line])):
        if maxValue < float(sentenceMatrix[line][i]):
            col = i
            maxValue = float(sentenceMatrix[line][i])
    return col

def segment(filePath, controlSeg, reverse):
    matrix = readMatrixFile(filePath)
    if not reverse:
        matrix = [list(i) for i in zip(*matrix)]
    finalString = ""
    lastCol = -1
    for i in range(1, len(matrix)): #for each element
        col = getMaxProbCol(i, matrix)
        if matrix[i][0] in controlSeg:
            finalString += " " + matrix[i][0]  + " "
        elif lastCol == -1: #first character
            finalString += matrix[i][0] #put the character in the beginning
        elif lastCol == col: # if the current character and the last one are not separated
            finalString += matrix[i][0]
        else:
            finalString += " " + matrix[i][0]
        lastCol = col
    finalString = finalString.replace("  "," ")
    if finalString[-1] == " ":
        finalString = finalString[:-1]
    if finalString[0] == " ":
        finalString = finalString[1:]
    return finalString

def writeOutput(finalString, output):
    with codecs.open(output, "a", "UTF-8") as outputFile:
        outputFile.write(finalString + "\n")

def readControlFile(inputPath):
	words = []
	with codecs.open(inputPath, "r", "UTF-8") as inputFile:
		for line in inputFile:
			for word in line.strip("\n").split("\t"):
				if not word in words:
					words.append(word)
	return words

def readFile(path):
    return [line.strip("\n") for line in codecs.open(path, "r","UTF-8")]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--matrices-folder', type=str, nargs='?', help='matrices folder')
    parser.add_argument('--output-file', type=str, nargs='?', help='name for the output name')
    parser.add_argument('reverse', type=bool, default=False, nargs='?', help='indicates if the matrix needs to be transposed before segmentation')
    parser.add_argument('--individual-files', type=str, nargs='?', help='list of names for generating individual files')
    parser.add_argument('--output-folder', type=str, nargs='?', help='folder for storing individual files')
    args = parser.parse_args()

    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(1)

    if args.matrices_folder and args.output_file:
        sentencesPaths = glob.glob(args.matrices_folder+"*.txt") #the seq2seq always produces matrices ending with .txt
        outputPath = args.output_file

        for index in range(1, len(sentencesPaths)+1):
            filePath = getPath(index, sentencesPaths)
            finalstr = segment(filePath, [], args.reverse).replace(" </S>","").replace("</S>","") #removing EOS
            writeOutput(finalstr, outputPath)

    if args.matrices_folder and args.individual_files and args.output_folder:
        sentencesPaths = glob.glob(args.matrices_folder+"*.txt") #the seq2seq always produces matrices ending with .txt
        files_output_list = readFile(args.files_output_list)
        folder = args.output_folder
        if folder[-1] != "/":
            folder+= "/"
        assert len(files_output_list) == len(sentencesPaths)

        for index in range(1, len(sentencesPaths)+1):
            filePath = getPath(index, sentencesPaths)
            finalstr = segment(filePath, [], args.reverse).replace(" </S>","").replace("</S>","") #removing EOS
            writeOutput(finalstr, folder + files_output_list[index-1].split("/")[-1] + ".hardseg")
            #writeOutput(finalstr, outputPath)

if __name__ == "__main__":
    main()
