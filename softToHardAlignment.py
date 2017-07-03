
import sys
import codecs
import glob

def getPath(number, paths):
    for path in paths:
        if "." + str(number) + "." in path:
            return path
    return None

def readMatrixFile(path):
    return [line.strip("\n").split("\t") for line in codecs.open(path,"r","UTF-8")]

def getMaxProbLine(column, sentenceMatrix):
    maxValue = float(sentenceMatrix[1][column]) #start from the first line after the characters
    line = 1
    for i in range(2, len(sentenceMatrix)):
        if maxValue < float(sentenceMatrix[i][column]):
            line = i
            maxValue = float(sentenceMatrix[i][column])
    return line

def segment(filePath, top100):
    matrix = readMatrixFile(filePath)
    finalString = ""
    lastLine = -1
    for i in range(1, len(matrix[0])): #for each element
        line = getMaxProbLine(i, matrix)
        if matrix[0][i] in top100:
            finalString += " " + matrix[0][i] + " "
        elif lastLine == -1: #first character
            finalString += matrix[0][i] #put the character in the beginning
        elif lastLine == line: # if the current character and the last one are not separated
            finalString += matrix[0][i]
        else:
            finalString += " " + matrix[0][i]
        lastLine = line
    finalString = finalString.replace("  "," ")
    if finalString[-1] == " ":
        finalString = finalString[:-1]
    if finalString[0] == " ":
        finalString = finalString[1:]
    return finalString

def writeOutput(finalString, output):
    with codecs.open(output, "a", "UTF-8") as outputFile:
        outputFile.write(finalString + "\n")

def readFile(inputPath):
    words = []
    with codecs.open(inputPath, "r", "UTF-8") as inputFile:
        for line in inputFile:
            words.append(line.strip("\n").split("\t"))
    return words

def main():
    sentencesPaths = glob.glob(sys.argv[1]+"*.txt")
    outputPath = sys.argv[2]
    controlFile = readFile(sys.argv[3])
    unseg = int(sys.argv[4])
    print len(sentencesPaths)
    if unseg == 1:
        top100 = []
    for index in range(1, len(sentencesPaths)+1):
        filePath = getPath(index, sentencesPaths)
        if unseg == 1:
            finalstr = segment(filePath, [])
        else:
            finalstr = segment(filePath, controlFile[index-1])
        writeOutput(finalstr, outputPath)



if __name__ == "__main__":
    main()
