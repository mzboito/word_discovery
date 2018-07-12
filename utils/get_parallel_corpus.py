import sys
import codecs

def read_file(path):
    return [line.strip("\n") for line in codecs.open(path, "r","UTF-8")]

def write_file(path, content):
    with codecs.open(path, "w", "UTF-8") as output_file:
        for c in content:
            output_file.write(c + "\n")

def get_parallel_files(ids_list, folder_lang1, folder_lang2, suffix_lang1, suffix_lang2):
    lang1 = []
    lang2 = []
    for file_name in ids_list:
        prefix = file_name.split(".")[0].split("/")[-1]
        lang1.append(read_file(folder_lang1 + prefix + suffix_lang1)[0])
        lang2.append(read_file(folder_lang2 + prefix + suffix_lang2)[0])
    return lang1, lang2

def main():
    if len(sys.argv) < 7:
        print "USAGE\t<dev_list> <train_list> <folder_lang1> <folder_lang2> <suffix_lang1> <suffix_lang2>\n"
        sys.exit(1)
    
    dev_list = read_file(sys.argv[1])
    train_list = read_file(sys.argv[2])
    folder_lang1 = sys.argv[3] if sys.argv[3][-1] == '/' else sys.argv[3] + '/'
    folder_lang2 = sys.argv[4] if sys.argv[4][-1] == '/' else sys.argv[4] + '/'
    suffix_lang1 = sys.argv[5]
    suffix_lang2 = sys.argv[6]

    dev_lang1, dev_lang2 = get_parallel_files(dev_list, folder_lang1, folder_lang2, suffix_lang1, suffix_lang2)
    train_lang1, train_lang2 = get_parallel_files(train_list, folder_lang1, folder_lang2, suffix_lang1, suffix_lang2)
    

    write_file("dev." + suffix_lang1, dev_lang1)
    write_file("dev." + suffix_lang2, dev_lang2)
    write_file("train." + suffix_lang1, train_lang1)
    write_file("train." + suffix_lang2, train_lang2)

        

if __name__ == '__main__':
    main()
