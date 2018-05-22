import sys 
import glob
import codecs

input_files = glob.glob(sys.argv[1] + "*")

for f in input_files:
    with codecs.open(f,"r","UTF-8") as inputFile:
        with codecs.open(sys.argv[2] + f.split("/")[-1] ,"w", "UTF-8") as outputFile:
            for line in inputFile:
                line = line.replace("\\","").replace("\'", "").replace("-","").replace("[","").replace(".","").replace("]","").replace("`","").replace("#","").replace("  "," ")
                outputFile.write(line)
