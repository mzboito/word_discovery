import sys
import codecs
import glob

threshold = float(sys.argv[3])

def read_file(path):
        return [line.strip("\n").split("\t") for line in codecs.open(path,"r","UTF-8")]

def step(matrix, segmentation):
    new_matrix = [[0]*len(matrix[0])]*len(matrix)
    diffs = [0]*len(matrix) #array for the differences for each character (matrix line)
    for line in range(1,len(matrix)): #for each line
        diffs[line] = calculateDiff(matrix[line])
    diffs = normalize(diffs,segmentation)
    new_segmentation =  getHardSegmentations(diffs, segmentation, matrix) #returns pairs of (symbol, alignment) as in ("a",3), which means a is aligned to the third word. If -1, it means it was not decided yet
    return smooth_submatrices(new_segmentation, matrix), new_segmentation

def calculateDiff(matrix_line):
    line = [0]*len(matrix_line)
    for i in range(1,len(matrix_line)):
        line[i] = float(matrix_line[i])
    highest = max(line)
    line.remove(highest)
    second = max(line)
    return highest*100 - second*100.0

def normalize(diffs,segmentation):
    unsegmented = []
    #print diffs
    for i in range(0, len(segmentation)):
        if segmentation[i][1] == -1:
            unsegmented.append(diffs[i])
    highest = max(unsegmented)
    if highest != 0:
        for i in range(1,len(diffs)):
            diffs[i] = diffs[i]/highest*1.0
    return diffs

def getHardSegmentations(diffs, segmentation, matrix):
    for i in range(1, len(diffs)):
        if diffs[i] > threshold:
            bucket = getBucket(matrix[i])
            segmentation[i][1] = bucket #(symbol, bucket)
    for i in range(1,len(segmentation)):
        if i == 1 and i+1 < len(segmentation) and segmentation[i][1] == -1 and segmentation[i+1][1] != -1: #then this character does not have a choice
            segmentation[i][1] = decideBucket(matrix[i],-1,segmentation[i+1][1])
        elif i+1 < len(segmentation) and segmentation[i][1] == -1 and segmentation[i+1][1] != -1 and segmentation[i-1][1] != -1:
            segmentation[i][1] = decideBucket(matrix[i],segmentation[i-1][1],segmentation[i+1][1])
        elif i+1 == len(segmentation) and segmentation[i-1][1] != -1:
            segmentation[i][1] = decideBucket(matrix[i],segmentation[i-1][1],-1)
    return segmentation

def getBucket(matrix_line):
    max_value = float(matrix_line[1])
    bucket = 1
    for i in range(2, len(matrix_line)):
        if float(matrix_line[i]) > max_value:
            max_value = float(matrix_line[i])
            bucket = i
    return bucket

def decideBucket(matrix_line, left, right):
    new_matrix = cleanMatrix(matrix_line, left, right)
    bucket = getBucket(new_matrix)
    return bucket

def cleanMatrix(matrix_line, left, right):
    for i in range(1, len(matrix_line)):
        if i != left and i != right:
            matrix_line[i] = 0.0
    return matrix_line

def smooth(matrix, header):
    new_matrix = [ [0 for _ in range(len(matrix[0]))] for _ in range(len(matrix)) ]
    for i in range(0, len(matrix)):
        new_matrix[i][0] = matrix[i][0]
    column_beginning = 1
    if header:
        line_beginning = 1
        new_matrix[0][0] = matrix[0][0] # adding the words to the new matrix
    else:
        line_beginning = 0

    for c in range(column_beginning,len(matrix[0])):
        for line in range(line_beginning, len(matrix)):
            #print matrix
            if len(matrix) == 2: #only one word
                    new_matrix = matrix
            elif line == 1:
                    new_matrix[line][c] = str((float(matrix[line][c]) + float(matrix[line+1][c]))/2)
            elif matrix[line][c] == matrix[-1][c]:
                    new_matrix[line][c] = str((float(matrix[line][c]) + float(matrix[line-1][c]))/2)
            else:
                    new_matrix[line][c] = str((float(matrix[line-1][c]) + float(matrix[line][c]) + float(matrix[line+1][c]))/3)
    return new_matrix

def smooth_submatrices(segmentation, matrix):
    ranges = getRanges(segmentation)
    for (beginning, ending) in ranges:
        matrix[beginning+1:ending] = smooth(matrix[beginning+1:ending],False)
    return matrix

def getRanges(segmentation):
    ranges = []
    between = False
    beginning = -1
    ending = -1
    for i in range(1, len(segmentation)):
        if (not between and segmentation[i][1] != -1) or i == 1:
            beginning = i
        elif segmentation[i][1] == -1:
            between = True
        elif between and segmentation[i][1] != -1:
            ending = i
            between = False
            ranges.append((beginning, ending))
        elif i+1 == len(segmentation) and between:
            ending = i
            ranges.append((beginning, ending))
    return ranges

def emptySegmentation(matrix):
    segmentation = []
    for i in range(0,len(matrix)):
        segmentation.append([matrix[i][0],-1])
    return segmentation

def softToHard(segmentation):
    string =""
    boundary = -1
    for i in range(1, len(segmentation)):
        if i == 1:
            string += segmentation[i][0]
            boundary = segmentation[i][1]
        elif segmentation[i][1] == -1 or segmentation[i][1] == boundary:
            string+= segmentation[i][0]
        else:
            string+= " " + segmentation[i][0]
            boundary = segmentation[i][1]
    return string

def writeOutput(finalString, output):
    with codecs.open(output, "a", "UTF-8") as outputFile:
        outputFile.write(finalString.replace("\n","") + "\n")

def main():
    paths = sys.argv[1]
    outputSeg = sys.argv[2]
    for i in range(1,4644):
        matrix = read_file(paths+"."+str(i)+".txt")
        step(matrix, emptySegmentation(matrix))
        new_matrix, segmentation = step(matrix, emptySegmentation(matrix))
        #print segmentation
        final_matrix, final_segmentation = step(new_matrix, segmentation)
        #print segmentation
        result = softToHard(final_segmentation)
        #print result
        writeOutput(result, outputSeg)


if __name__ == '__main__':
    main()

#### post proc
