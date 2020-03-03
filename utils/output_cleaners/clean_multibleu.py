import sys
bleu = [line.strip() for line in open(sys.argv[1])][0].split(", ")
with open(sys.argv[1]+".OUTPUT","w") as output_file:
    output_file.write(bleu[0].replace("BLEU = ","") + "\t" + bleu[1].split(" ")[0]+"\n")