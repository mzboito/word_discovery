# -*- coding: utf-8 -*-

import sys
import codecs
import glob

def averageMatrices(s2t, t2s):
    for i in range(1, len(s2t)):
        for j in range(1, len(s2t[0])):
            s2t[i][j] = str((float(s2t[i][j]) + float(t2s[j][i]))/2)
    return s2t

def writeOutput(path, s2t):
    with codecs.open(path, "w", "UTF-8") as outputFile:
        for line in range(0, len(s2t)):
            outputFile.write("\t".join(line) + "\n")

def readMatrixFile(path):
    return [line.strip("\n").split("\t") for line in codecs.open(path,"r","UTF-8")]

def main():
    source2target_folder = sys.argv[1]
    target2source_folder = sys.argv[2]
    output_folder = sys.argv[3]

    source2target_matrices = glob.glob(sys.argv[1]+"*.txt")

    for s2t_matrix in source2target_matrices:
        file_name = s2t_matrix.split("/")[-1]
        print file_name
        s2t = readMatrixFile(s2t_matrix)
        t2s = readMatrixFile(target2source_folder + file_name)
        print len(s2t), len(s2t[0])
        print len(t2s), len(t2s[0])
        s2t_avg = averageMatrices(s2t, t2s)
        writeOutput(output_folder + file_name, s2t)

if __name__ == '__main__':
    main()
