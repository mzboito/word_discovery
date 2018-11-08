import sys
import codecs

def read_file(f_path):
    return [line.strip("\n") for line in codecs.open(f_path, "r", "utf-8")]

def get_max_length(ids_list):
    max_l = 1
    for i in range(len(ids_list)):
        c = len(ids_list[i])
        if c > max_l:
            max_l = c
    return max_l

def format_id(f_path):
    ids = read_file(f_path)
    max_l = get_max_length(ids)
    for i in range(len(ids)):
        ids[i] = "0"*(max_l-len(ids[i])) + ids[i]
    return ids

def write_output(f_path, ids_list):
    with codecs.open(sys.argv[1],"r","utf-8") as output_file:
        for line in ids_list:
            output_file.write(line + "\n")

def main():
    id_file = sys.argv[1]
    output_file = id_file + ".format"
    write_output(output_file, format_id(id_file))

if __name__ == '__main__':
    main()