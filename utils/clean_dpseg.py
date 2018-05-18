import codecs
import sys


dpseg_out = [line for line in codecs.open(sys.argv[1], "r", "UTF-8", errors="replace")]


flag = False
with codecs.open(sys.argv[2], "w", "UTF-8") as outputFile:
    for i in range(len(dpseg_out)):
        if "_nstrings=xxx" in dpseg_out[i]:
            break
        if flag:
            outputFile.write(dpseg_out[i])
        if "State:" in dpseg_out[i]:
            flag = True
