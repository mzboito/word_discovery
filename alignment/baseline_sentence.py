# -*- coding: utf-8 -*-

import sys
import codecs
import math
import glob

#PH = "a0 a1 a19 a20 a25 a14 a45 a9 a9 a18 a33 a9 a27 a26 a7 a2 a30 a43 a31 a15 a13 a28 a10 a37 a31 a34 a35 a12 a42 a41 a35 a38 a12 a45 a29 a30 a41 a32 a37 a28 a7 a10 a34 a42 a3 a9 a39 a44 a6"
#FR = "je te remercie pour le bien que tu m&apos; as fait"

def segment(ph, fr, output_name):
    #create two lists
    ph_list = ph.strip().split(" ")
    fr_list = fr.replace("&apos;","\'").strip().split(" ")
    fr_list_size = len(fr_list)
    #get proportion of number of phonemes per symbol
    ph_number = len(ph_list) #phones number
    gr_number = len(fr.replace("&apos;","\'").strip().replace(" ","")) #graphemes number
    #get proportion ph_number / gr_number
    ph_per_grapheme = int(math.floor(ph_number/float(gr_number)))
    #print ph_number, gr_number, ph_per_grapheme, ph_per_grapheme * gr_number
    #check the remain
    rest = ph_number - ph_per_grapheme*gr_number
    ph_per_word = 0
    if(rest > 0): #if we cannot separate in equal parts
        fr_words = len(fr.split(" "))
        #print fr_words, rest, rest > fr_words, rest/fr_words
        if(rest >= fr_words):
            ph_per_word = int(rest/fr_words) #if we have a remain, adds ph per word
    #print ph_per_word
    index = 0
    with codecs.open(output_name, "w", "UTF-8") as out:
        for word in fr_list:
            w_length  = len(word)
            this_ph = (ph_per_grapheme * w_length) + ph_per_word
            #print word, w_length, this_ph
            i = index
            while(i < (this_ph + index) and i < ph_number):
                out.write(ph_list[i])
                i+=1
            if(word != fr_list[fr_list_size-1]):
                out.write(" ")
            index += this_ph
        while(index < ph_number):
            out.write(ph_list[index])
            index+=1
        out.write("\n")

def read_file(path):
    return [line for line in codecs.open(path,"r","uTF-8")]

def main():
    files_list = read_file(sys.argv[1]) #get all the lines
    ph_list = read_file(sys.argv[2])
    fr_list = read_file(sys.argv[3])
    out_dir = sys.argv[4]
    #files = glob.glob(out_dir + ".lab")

    if(len(files_list) == len(ph_list) and len(ph_list )== len(fr_list)):
        for i in range(0, len(files_list)):
            segment(ph_list[i], fr_list[i], out_dir + files_list[i].split(".lab")[0] + ".baseline")

if __name__ == '__main__':
    main()

