import codecs
import sys

def unseg_with_boundary(lang):
    unseg = []
    for sentence in lang:
        line = sentence.replace(" ","_B_").strip()
        new_sentence = line[0]
        for i in range(1,len(line)):
            new_sentence += " " + line[i]
        unseg.append(new_sentence + "\n")
    return unseg


def read_file(path):
	return [line for line in codecs.open(path,"r","UTF-8")]

def write_file(output_name, sentences):
    with codecs.open(output_name, "r", "utf-8") as outputFile:
        for sentence in sentences:
            outputFile.write(sentence)

def main():
    sentences = read_file(sys.argv[1])
    write_file(sys.argv[2], unseg_with_boundary(sentences))

if __name__ == '__main__':
    main()