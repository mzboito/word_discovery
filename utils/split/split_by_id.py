import sys
import codecs

SRC_EXT = ".lab"
TGT_EXT = ".fr"


def read_file(f_path):
    return [line for line in codecs.open(f_path, "r", "utf-8")]

def write_file(f_path, sentence):
    with codecs.open(f_path, "w","utf-8") as output_file:
        output_file.write(sentence)

def main():
    source = read_file(sys.argv[1])
    target = read_file(sys.argv[2])
    labs = read_file(sys.argv[3])
    output_dir = sys.argv[4]
    assert len(source) == len(target) and len(target) == len(labs)
    for i in range(len(labs)):
        name = output_dir + (labs[i].strip("\n").split(".")[0])
        write_file(name + SRC_EXT, source[i])
        write_file(name + TGT_EXT, target[i])

if __name__ == '__main__':
    main()