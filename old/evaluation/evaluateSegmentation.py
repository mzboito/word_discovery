
import sys
import codecs

# RECALL: NUMBER OF CORRECTLY SEGMENTED / TOTAL NUMBER IN THE GOLD STANDARD

# PRECISION: NUMBER OF CORRECTLY SEGMENTED / NUMBER OF SEGMENTATIONS CREATED

# F-SCORE: 2*RECALL*PRECISION / (PRECISION + RECALL)

def getScore(mboshiGold, mboshiExp):
    mboshiWords = mboshiGold.split(" ")
    mboshiExpWords = mboshiExp.split(" ")
    score = 0
    for word in mboshiExpWords:
        if word in mboshiWords:
            mboshiWords.remove(word) #avoid multiples matches for incorrect substrings
            score += 1
    return score

def getScoreTop100(mboshiGold, mboshiExp, mboshiControl):
    mboshiWords = mboshiGold.split(" ")
    mboshiExpWords = mboshiExp.split(" ")
    score = 0
    for word in mboshiExpWords:
        if word in mboshiWords and word in mboshiControl:
            mboshiWords.remove(word) #avoid multiples matches for incorrect substrings
            score += 1
    return score

def evaluateTokens(mboshiGold, mboshiUnsupervised, mboshiControl):
    numberTokensGold = 0
    numberTokensUnsup = 0
    numberCorrectTokens = 0
    numberCorrectTop100 = 0
    numberCorrectRest = 0

    for i in range(0, len(mboshiGold)):
        lineGold = len(mboshiGold[i].split(" ")) #number of tokens in the line
        lineUnsupervised = len(mboshiUnsupervised[i].split(" ")) #number of created segmentations
        correctlySegmented = getScore(mboshiGold[i], mboshiUnsupervised[i]) #number of tokens found
        correctlyInTop100 = getScoreTop100(mboshiGold[i], mboshiUnsupervised[i], mboshiControl[i]) #number of tokens in top100

        numberTokensGold += lineGold
        numberTokensUnsup += lineUnsupervised
        numberCorrectTokens += correctlySegmented
        numberCorrectTop100 += correctlyInTop100
        numberCorrectRest += correctlySegmented - correctlyInTop100

        if (correctlySegmented - correctlyInTop100) < 0:
            print "ERROR"
            sys.exit(1)

    #recall
    recall = float(numberCorrectTokens) / numberTokensGold
    #precision
    precision = float(numberCorrectTokens) / numberTokensUnsup
    #f-score
    fscore = 2.0*recall*precision / (precision + recall)

    return [recall, precision, fscore, numberTokensGold, numberTokensUnsup, numberCorrectTokens, numberCorrectTop100, numberCorrectRest]

def getTypes(sentencesList):
    types = []
    for i in range(0, len(sentencesList)):
        for word in sentencesList[i].split(" "):
            if not word in types:
                types.append(word)
    return types

def filterTypes(gold, words):
    newWords = []
    for word in words:
        if word in gold:
            newWords.append(word)
    return newWords

def evaluateTypes(mboshiGold, mboshiUnsupervised, mboshiTop100):
    typesGold = getTypes(mboshiGold)
    typesUnsup = getTypes(mboshiUnsupervised)
    correctTypes = filterTypes(typesGold, typesUnsup)
    correctTop100 = filterTypes(mboshiTop100, typesUnsup)

    numberTypesGold = len(typesGold)
    numberTypesUnsup = len(typesUnsup)
    numberCorrectTypes = len(correctTypes)
    numberCorrectTop100 = len(correctTop100)
    numberCorrectRest = numberCorrectTypes - numberCorrectTop100

    if numberCorrectTypes < numberCorrectTop100:
        print "ERROR"
        sys.exit(1)

    recall = numberCorrectTypes / float(numberTypesGold)
    precision = numberCorrectTypes / float(numberTypesUnsup)
    fscore = 2.0*recall*precision / (precision + recall)

    return [recall, precision, fscore, numberTypesGold, numberTypesUnsup, numberCorrectTypes, numberCorrectTop100, numberCorrectRest]

def evaluate(mboshiGold, mboshiUnsupervised, mboshiControl, mboshiTop100):
    resultsToken = evaluateTokens(mboshiGold, mboshiUnsupervised, mboshiControl)
    resultsType = evaluateTypes(mboshiGold, mboshiUnsupervised, mboshiTop100)
    return [resultsToken, resultsType]

def writeOutput(outputPath, results):
    for i in range(0, len(results[0])):
        results[0][i] = str(results[0][i])
        results[1][i] = str(results[1][i])
    with open(outputPath, "w") as outputFile:
        outputFile.write("\t".join(["Eval", "Recall", "Precision", "F-score", "Gold Count", "Unsupervised Count", "Total Correct", "In top100", "Not in top100"]) + "\n")
        outputFile.write("TOKENS\t"+"\t".join(results[0])+"\n")
        outputFile.write("TYPES\t"+"\t".join(results[1])+"\n")

def readFile(inputPath):
    return [line.strip("\n") for line in codecs.open(inputPath, "r", "UTF-8")]

def getTop100(mboshiControl):
    top100 = []
    for words in mboshiControl:
        for w in words.split("\t"):
            if w != u'' and not w in top100:
                top100.append(w)
    return top100

def main():
    mboshiGold = readFile(sys.argv[1])
    mboshiUnsupervised = readFile(sys.argv[2])
    mboshiControl = readFile(sys.argv[3])
    mboshiTop100 = getTop100(mboshiControl)
    outputPath = sys.argv[4]
    if len(mboshiGold) == len(mboshiUnsupervised):
        results = evaluate(mboshiGold, mboshiUnsupervised, mboshiControl, mboshiTop100)
        writeOutput(outputPath, results)

if __name__ == '__main__':
    main()
