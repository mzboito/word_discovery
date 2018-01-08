import sys
import codecs

with codecs.open(sys.argv[1],"r", "UTF-8") as inputFile:
    with codecs.open(sys.argv[2], "w", "UTF-8") as outputFile:
        for line in inputFile:
		#rint line
		line = line.replace(" </S>","")
		line = line.replace("</S>","")
		#rint line          
		outputFile.write(line)
