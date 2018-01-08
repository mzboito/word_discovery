
import sys
import codecs
import glob

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

def writeOutput(finalString, output, path):
    with codecs.open(output + path.split("/")[-1], "w", "UTF-8") as outputFile:
        outputFile.write(finalString + "\n")

def main():
    sentencesPaths = glob.glob(sys.argv[1]+"*.txt")
    outputPath = sys.argv[2]
    for path in sentencesPaths:
        finalstr = segment(path, []).replace(" </S>","").replace("</S>","")
        writeOutput(finalstr, outputPath, path.replace(".txt", ""))


if __name__ == "__main__":
    main()
