import sys
import codecs

EOS_symbol = "</S>"
BOS_symbol = "<S>"
UNK_symbol = "<UNK>"

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