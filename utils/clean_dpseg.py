import codecs
import sys


dpseg_out = [line for line in codecs.open(sys.argv[1], "r", "UTF-8")]


flag = False
with codecs.open(sys.argv[2], "w", "UTF-8") as outputFile:
    for i in range(len(dpseg_out)):
        if "_nstrings=xxx" in line[i]:
            break
        if flag:
            outputFile.write(line)
        if "State:" in line[i]:
            flag = True
