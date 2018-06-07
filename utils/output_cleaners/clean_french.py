import sys
import codecs


with codecs.open(sys.argv[1], "r","UTF-8") as inputFile:
    with codecs.open(sys.argv[1]+".clean", "r", "UTF-8") as outputFile:
        for line in inputFile:
            line = line.strip("\n").replace("&apos;"," ").replace("."," ").replace(";"," ").replace(","," ")
            while "  " in line:
                line = line.replace("  "," ")
            if len(line) > 0:
                while line[0] == " ":
                    line = line[1:]
                while line[-1] == " ":
                    line = line[:-1]
            outputFile.write(line + "\n")
            
              

