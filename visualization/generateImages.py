# -*- coding: utf-8 -*-

import sys
import os
from logParser import LogParser


def get_script_path():
    script_file = sys.argv[0]
    if len(script_file.split("/")) > 1:
        return "/".join(script_file.split("/")[:-1])
    else:
        return os.getcwd()

def call_R(log_out_path, output, dev_and_train):
    script_path = get_script_path()
    os.system("Rscript --vanilla %s/createGraphics.r %s %s %d" % (script_path, log_out_path, output, dev_and_train))

def print_usage():
    print "python generateImages.py <log path> <output folder> <dev and train>\n"
    print "\t<log path> path to the log file\n"
    print "\t<output folder> path to the folder where the images will be stored\n"
    print "\t<dev and train> 1: only dev, 2: dev and train\n"

def main():
    if len(sys.argv) < 4:
        print_usage()
        exit(1)
    log_file = sys.argv[1]
    folder_output = sys.argv[2]
    if folder_output == ".":
        folder_output+="/"
    try:
        dev_and_train = int(sys.argv[3])
    except Exception:
        print "Problem converting <dev and train> parameter \n"
        print_usage()
        exit(1)

    prefix = log_file.split("/")[-1]
    log_out_name =  prefix + ".out"
    log_out_path = folder_output + log_out_name
    p = LogParser(log_file, log_out_path, dev_and_train)
    p.write_out()

    if folder_output[-1] == "/":
        folder_output = folder_output + prefix
    else:
        folder_output = folder_output + "/" + prefix

    call_R(log_out_path, folder_output, dev_and_train)


if __name__ == '__main__':
    main()