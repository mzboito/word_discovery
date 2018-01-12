# -*- coding: utf-8 -*-

import sys
import codecs
import math
import glob

#PH = "a0 a1 a19 a20 a25 a14 a45 a9 a9 a18 a33 a9 a27 a26 a7 a2 a30 a43 a31 a15 a13 a28 a10 a37 a31 a34 a35 a12 a42 a41 a35 a38 a12 a45 a29 a30 a41 a32 a37 a28 a7 a10 a34 a42 a3 a9 a39 a44 a6"
#FR = "je te remercie pour le bien que tu m&apos; as fait"

def segment(ph, target):
    #create two lists
    ph_list = ph.strip().split(" ")
    target_list = target.replace("&apos;","\'").strip().split(" ")
    target_list_size = len(target_list)
    #get proportion of number of phonemes per symbol
    ph_number = len(ph_list) #phones number
    gr_number = len(target.replace("&apos;","\'").strip().replace(" ","")) #graphemes number
    #get proportion ph_number / gr_number
    ph_per_grapheme = int(math.floor(ph_number/float(gr_number)))
    #print ph_number, gr_number, ph_per_grapheme, ph_per_grapheme * gr_number
    #check the remain
    rest = ph_number - ph_per_grapheme*gr_number
    ph_per_word = 0
    if(rest > 0): #if we cannot separate in equal parts
        target_words = len(target.split(" "))
        #print target_words, rest, rest > target_words, rest/target_words
        if(rest >= target_words):
            ph_per_word = int(rest/target_words) #if we have a remain, adds ph per word
    #print ph_per_word
    index = 0
    segmentation = ""
    for word in target_list:
        w_length  = len(word)
        this_ph = (ph_per_grapheme * w_length) + ph_per_word
        #print word, w_length, this_ph
        i = index
        while(i < (this_ph + index) and i < ph_number):
            segmentation+=ph_list[i]
            i+=1
        if(word != target_list[target_list_size-1]): #it it is not in the end
            segmentation += " "
        index += this_ph
    while(index < ph_number): #the rest
        segmentation += ph_list[index]
        index+=1
    return segmentation

def write_file(path, sentences):
    with codecs.open(path, "w", "UTF-8") as out:
        for sentence in sentences:
            out.write(sentence + "\n")

def read_file(path):
    return [line for line in codecs.open(path,"r","uTF-8")]

def print_usage():
    print "Proportional baseline - corpus version \n"
    print "arg1: unsegmented source (with blank spaces between the symbols)\narg2: aligned target translation\narg3: output file name\n"

def main():
    if len(sys.argv) < 4:
        print_usage()
        sys.exit(1)
    source_list = read_file(sys.argv[1])
    target_list = read_file(sys.argv[2])
    out_file = sys.argv[3]

    if(len(source_list) == len(target_list)):
        sentences = []
        for i in range(0, len(source_list)):
            sentences.append(segment(source_list[i], target_list[i]))
        write_file(out_file, sentences)

if __name__ == '__main__':
    main()
