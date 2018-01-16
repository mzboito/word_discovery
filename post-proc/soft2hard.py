## for the moment just works for reverse architecture

import sys
import codecs
import glob

def getPath(number, paths):
    for path in paths:
        if "." + str(number) + "." in path:
            return path
    return None

def readMatrixFile(path):
    #print path
    return [line.strip("\n").split("\t") for line in codecs.open(path,"r","UTF-8")]

def getMaxProbCol(line, sentenceMatrix):
    maxValue = float(sentenceMatrix[line][1]) #start from the first line after the characters
    col = 1
    for i in range(2, len(sentenceMatrix[line])):
        if maxValue < float(sentenceMatrix[line][i]):
            col = i
            maxValue = float(sentenceMatrix[line][i])
    return col

def segment(filePath, top100):
    matrix = readMatrixFile(filePath)
    finalString = ""
    lastCol = -1
    for i in range(1, len(matrix)): #for each element
        col = getMaxProbCol(i, matrix)
        if matrix[i][0] in top100:
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

def print_usage():
    print "soft2hard for corpus"
    print "arg1: matrices folder\narg2: output file\n"

def main():
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)
    sentencesPaths = glob.glob(sys.argv[1]+"*.txt") #the seq2seq always produces matrices ending with .txt
    outputPath = sys.argv[2]
    for index in range(1, len(sentencesPaths)+1):
        filePath = getPath(index, sentencesPaths)
        finalstr = segment(filePath, []).replace(" </S>","").replace("</S>","") #removing EOS
        writeOutput(finalstr, outputPath)



if __name__ == "__main__":
    main()
