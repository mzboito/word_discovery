import sys
import codecs


def write_output(path, dictionary):
    with codecs.open(path,"w","utf-8") as output_file:
        keys = sorted(list(dictionary.keys()))
        for key in keys:
            output_file.write("{}\t{}\n".format(key, dictionary[key]))


def main():
    #sentences = read_file(sys.argv[1])
    COUNT = dict()
    with codecs.open(sys.argv[1], "r","utf-8") as input_file:
        for line in input_file:
            token = line.strip("\n").split(" ")[-1]
            length = len(token)
            if token == "SIL":
                token = "s"
                #pass
            elif length in COUNT:
                COUNT[length] +=1
            else:
                COUNT[length] = 1
    write_output(sys.argv[2],COUNT)

if __name__ == '__main__':
    main()