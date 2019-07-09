import sys
import codecs, glob

EOS_symbol = "</S>"
BOS_symbol = "<S>"
UNK_symbol = "<UNK>"
SIL_symbol = "SIL"
transformer_decoder = {"TransformerDecoder":["EncoderDecoderAttention"]}
transformer_coders = {"TransformerEncoder":["SelfAttention"], "TransformerDecoder":["SelfAttention", "EncoderDecoderAttention"]}

def read_file(path):
    return [line.strip("\n") for line in codecs.open(path, "r","UTF-8")]

def read_lab_files(path):
    '''
    returns a dictionary containing the indexes of the phones that come before a silence
    '''
    dictionary = dict()
    f_paths = glob.glob(path + "/*")
    for f_path in f_paths:
        labs = read_file(f_path)
        s_id = ".".join(f_path.split("/")[-1].split(".")[:-1])
        dictionary[s_id] = list()
        for element in labs:
            #input example: 1.5400 1.7200 phn2\n1.7200 2.1400 SIL\n
            phone = element.split(" ")[-1]
            duration = element.split(" ")[:-1]
            dictionary[s_id].append([phone, duration])
    return dictionary

def read_matrix_file(path):
    return [line.strip("\n").split("\t") for line in codecs.open(path,"r","UTF-8")]

def clean_line(inputStr):
    inputStr = inputStr.replace(UNK_symbol,"").replace(EOS_symbol,"").replace(BOS_symbol,"")
    while inputStr and inputStr[0] == " ":
        inputStr = inputStr[1:]
    while("  " in inputStr):
        inputStr = inputStr.replace("  "," ")
    return inputStr

def folder(f_str):
    return f_str if f_str[-1] == "/" else f_str + "/"

def generate_heads(number, avg_flag=False):
    if not avg_flag or number == 1:
        return ["head"+str(i+1) for i in range(number)] 
    else:
        return ["avg"] + ["head"+str(i+1) for i in range(number)]

def generate_attn2d_folders(number):
    folders = ["final"]
    for i in range(1,number):
        folders.append("raw_attn_layer_" + str(i))
    return folders

def get_path(number, paths, transformer=False, pervasive=False):
    if transformer or pervasive:
        token = "_" if transformer else "."
        for path in paths:
            if str(number) == path.split("/")[-1].split(token)[0]: 
                return path
    else:
        for path in paths:
            if "." + str(number) + "." in path:
                return path
    raise Exception("Path not found")

def write_output_matrix(path, matrix):
	with codecs.open(path, "w", "UTF-8") as outputFile:
		for line in matrix:
			outputFile.write("\t".join(line) + "\n")

def write_output(finalString, output, mode="w"):
    with codecs.open(output, mode, "UTF-8") as outputFile:
        outputFile.write(finalString + "\n")


def write_file(f_name, lst):
    with codecs.open(f_name,"w",'utf-8') as output_file:
        for element in lst:
            output_file.write(element + "\n")

def write_dictionary(f_path, dictionary):
    with open(f_path, "w") as output_file:
        for key in dictionary.keys():
            if isinstance(dictionary[key], list):
                str_entry = ["\t".join([str(dictionary[key][0]), dictionary[key][1]])]
                output_file.write("\t".join([key] + str_entry) + "\n")
            else:
                output_file.write("\t".join([key, str(dictionary[key])]) + "\n")