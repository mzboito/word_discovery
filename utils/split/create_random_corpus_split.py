import sys
import codecs
from random import shuffle

''' CHANGE HERE TO USE WITH A DIFFERENT CORPUS: MBOSHI SETUP '''
DEV_SIZE = 514
TRAIN_SIZE = 4616
SUFIX = [".fr", ".ph"]
NUM_RANDOM = 5
''' '''

def read_parallel_data(lang1_path, lang2_path, list_path):
    sentences = []
    with codecs.open(lang1_path,"r","UTF-8") as lang1Input:
        with codecs.open(lang2_path,"r","UTF-8") as lang2Input:
            with codecs.open(list_path,"r","UTF-8") as listInput:
                for i in range(0,(DEV_SIZE+TRAIN_SIZE)):
                    try:
                        sentences.append([lang1Input.readline(), lang2Input.readline(), listInput.readline()])
                    except Exception:
                        print "Problem reading parallel files. Make sure they have the same length!\n"
                        print "The files must be %d lines long.\n" % (DEV_SIZE + TRAIN_SIZE)
    return sentences
                    
def write_random_files(sentences, output_folder):
    for i in range(1,NUM_RANDOM+1):
        with codecs.open(output_folder + "dev.rand"+str(i)+SUFIX[0],"w","UTF-8") as lang1Dev:
            with codecs.open(output_folder + "dev.rand"+str(i)+SUFIX[1],"w","UTF-8") as lang2Dev:
                with codecs.open(output_folder + "dev.rand"+str(i)+ ".ids","w","UTF-8") as listDev:
                    with codecs.open(output_folder + "train.rand"+str(i)+SUFIX[0],"w","UTF-8") as lang1Train:
                        with codecs.open(output_folder + "train.rand"+str(i)+SUFIX[1],"w","UTF-8") as lang2Train:
                            with codecs.open(output_folder + "train.rand"+str(i)+".ids","w","UTF-8") as listTrain:
                                shuffle(sentences) #different shuffle per rand version
                                for j in range(0, len(sentences)):
                                    if j < DEV_SIZE:
                                        lang1Dev.write(sentences[j][0])
                                        lang2Dev.write(sentences[j][1])
                                        listDev.write(sentences[j][2])
                                    else:
                                        lang1Train.write(sentences[j][0])
                                        lang2Train.write(sentences[j][1])
                                        listTrain.write(sentences[j][2])


def main():
    if len(sys.argv) < 5:
        print "USAGE: python create_random_corpus_split.py <corpus lang1> <corpus lang2> <list of files names> <output_folder>\n\n"
	sys.exit(1)
    sentences = read_parallel_data(sys.argv[1], sys.argv[2], sys.argv[3])
    write_random_files(sentences, sys.argv[4] if sys.argv[4][-1] == '/' else sys.argv[4]+'/')

if __name__ == '__main__':
    main()
