import sys
import codecs
from random import shuffle

PERCENTAGE = 10
SUFFIXES = ["id", "gold", "it"]

def write_file(output_path, l_range, l_lists, index):
    with codecs.open(output_path + SUFFIXES[index], "w", "UTF-8") as output_path:
        for j in range(l_range[0], l_range[1]):
            output_path.write(l_lists[j][index])


def write_files(output_path, l_range, l_lists):
    for index in range(len(SUFFIXES)):
        write_file(output_path, l_range, l_lists, index)

    
def main():
    id_path = sys.argv[1]
    lang1_path = sys.argv[2]
    lang2_path = sys.argv[3]
    output_path = sys.argv[4]
    if output_path[-1] != '/':
        output_path += '/'

    ids = [line for line in codecs.open(id_path,"r","UTF-8")]
    lang1 = [line for line in codecs.open(lang1_path,"r","UTF-8")]
    lang2 = [line for line in codecs.open(lang2_path,"r","UTF-8")]

    assert len(ids) == len(lang1) and len(lang1) == len(lang2) 

    parallel_list = []
    for index in range(len(ids)):
        parallel_list.append( [ids[index], lang1[index], lang2[index]] )
    
    shuffle(parallel_list)

    total_size = len(ids)
    dev_size = int(PERCENTAGE * total_size / 100.0)

    #for index in range(dev_size):
    write_files(output_path + "dev.", [0, dev_size], parallel_list)
    
    #for index in range(dev_size, total_size):
    write_files(output_path + "train.", [dev_size, total_size], parallel_list)



if __name__ == '__main__':
    main()
