import sys
import codecs

EOS_symbol = "</S>"
BOS_symbol = "<S>"
UNK_symbol = "<UNK>"
transformer_decoder = {"TransformerDecoder":["EncoderDecoderAttention"]}
transformer_coders = {"TransformerEncoder":["SelfAttention"], "TransformerDecoder":["SelfAttention", "EncoderDecoderAttention"]}

def read_file(path):
    return [line.strip("\n") for line in codecs.open(path, "r","UTF-8")]

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


def write_output_matrix(path, matrix):
	with codecs.open(path, "w", "UTF-8") as outputFile:
		for line in matrix:
			try:
				outputFile.write("\t".join(line) + "\n")
			except TypeError:
				exit(1)
