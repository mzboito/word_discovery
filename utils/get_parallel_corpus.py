import sys
import codecs

def read_file(path):
    return [line.strip("\n") for line in codecs.open(path, "r","UTF-8")]

def write_file(path, content):
    with codecs.open(path, "w", "UTF-8") as output_file:
        for c in content:
            output_file.write(c + "\n")

def main():
    if len(sys.argv) < 7:
        print "USAGE\t<ids_list> <folder_lang1> <folder_lang2> <suffix_lang1> <suffix_lang2> <output_prefix>\n"
        sys.exit(1)
    
    ids_list = read_file(sys.argv[1])
    folder_lang1 = sys.argv[2] if sys.argv[2][-1] == '/' else sys.argv[2] + '/'
    folder_lang2 = sys.argv[3] if sys.argv[3][-1] == '/' else sys.argv[3] + '/'
    suffix_lang1 = sys.argv[4]
    suffix_lang2 = sys.argv[5]

    lang1 = []
    lang2 = []
    for file_name in ids_list:
        prefix = file_name.split(".")[0].split("/")[-1]
        lang1.append(read_file(folder_lang1 + prefix + suffix_lang1)[0])
        lang2.append(read_file(folder_lang2 + prefix + suffix_lang2)[0])
    
    write_file(sys.argv[6] + suffix_lang1, lang1)
    write_file(sys.argv[6] + suffix_lang2, lang2)
        

if __name__ == '__main__':
    main()
