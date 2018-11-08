import sys
import utils
import codecs, glob, math
import Entropy
import numpy as np
from soft2hard import segment_target
import argparse

IDS_suffix = ".ids"
seg_suffix = ".hs"
sets = ["dev", "train"]
#target = True


'''
1) generate matrices with entropy per line
2) generate average entropy per matrix
3) generate average and number of tokens per matrix
4) generate classes (entropy buckets) files listing the files inside and count 
'''

class Matrix():
    def __init__(self, filepath, target, ids_dictionary):
        self.lines = utils.read_matrix_file(filepath)
        self.tokens = segment_target(self.lines, target).split(" ")
        self.entropies = self.calculate_entropies(self.lines)
        self.file_name = filepath.split("/")[-1]
        self.set = self.file_name.split(".")[0]
        self.index = int(self.file_name.split(".")[1])
        try:
            self.id = ids_dictionary[self.set][self.index-1]
        except KeyError:
            self.id = None
            print("Problem with id file, setting id to None")
    
    @staticmethod
    def calculate_entropies(matrix):
        entropies = []
        for i in range(1,len(matrix)): #for each line (first one is the list of words)
                phone_dist = Entropy.format_distribution(matrix[i])
                ent = Entropy.entropy(phone_dist)
                entropies.append(ent)
        return entropies
    

    def average_entropy(self):
        return sum(self.entropies) / len(self.entropies)
    
    def number_tokens(self):
        return len(self.tokens)
    
    def average_length(self):
        acc = 0
        for t in self.tokens:
            acc += len(t)
        return acc/len(self.tokens)
    
    def write_matrix(self, folder):
        with codecs.open(folder + self.file_name, "w","utf-8") as output_file:
            output_file.write("\t".join(self.lines[0] + ["Entropy"]) + "\n")
            for i in range(1,len(self.lines)):
                output_file.write("\t".join(self.lines[i] + [str(self.entropies[i-1])]) + "\n")
    

class Corpus():
    def __init__(self, matrices_path, target, ids_path):
        self.matrices = []
        for matrix_path in matrices_path:
            if ids_path:
                self.matrices.append(Matrix(matrix_path, target,self.read_ids(ids_path)))
            else:
                self.matrices.append(Matrix(matrix_path, target,dict()))

    def read_ids(self, ids_path):
        ids = dict()
        for id_set in sets:
            id_list = utils.read_file(ids_path + id_set + IDS_suffix)
            ids[id_set] = id_list
        return ids

    def reduce_buckets(self, dictionary, number_buckets):
        bucket = 1
        new_buckets = dict({bucket:[]})
        size_buckets = len(self.matrices) / number_buckets
        keys = sorted(dictionary.keys())
        for key in keys:
            for element in dictionary[key]:
                if len(new_buckets[bucket]) < size_buckets or bucket == size_buckets:
                    new_buckets[bucket].append(element)
                else:
                    bucket+=1
                    new_buckets[bucket] = [element]
        return new_buckets

    def get_average(self):
        acc = 0.0
        for m in self.matrices:
            acc += m.average_entropy()
        return acc / len(self.matrices)

    def print_average(self):
        print(self.get_average())
    
    def generate_buckets(self, precision):
        buckets = dict()
        for m in self.matrices:
            avg = round(m.average_entropy(),precision)
            if avg in buckets:
                buckets[avg].append(m)
            else:
                buckets[avg] = [m]
        return buckets

    def average_from_group(self, m_list, function):
        acc = 0
        for m in m_list:
            acc += function(m)
        return acc / len(m_list)

    def write_invidual_files(self, folder):
        for m in self.matrices:
            m.write_matrix(folder)

    def write_summary(self, f_name):
        with open(f_name, "w") as output_file:
            output_file.write("{}\t{}\t{}\t{}\n".format("id", "avg_entropy", "#tokens","avg_token_length"))
            for m in self.matrices:
                output_file.write("%s\t%.2f\t%.2f\t%.2f\n" %(m.file_name, m.average_entropy(), m.number_tokens(), m.average_length()))
      
    def write_buckets(self, f_name, precision=2, verbose=False):
        d = self.generate_buckets(precision)
        keys = sorted(d.keys())
        with open(f_name, "w") as output_file:
            output_file.write("group\tmembers\ttoken\tlength\n")
            for key in keys:
                output_file.write("{}\t{}\t{}\t{}\n".format(key, len(d[key]), 
                    round(self.average_from_group(d[key], Matrix.number_tokens), precision), round(self.average_from_group(d[key], Matrix.average_length), precision)))
                if verbose:
                    for m in d[key]:
                        output_file.write("\t{}\t{}\n".format(m.file_name, m.average_entropy()))
                    output_file.write("\n")
    
    def write_zrc_buckets(self, zrc_path, f_name, number_buckets, precision=2):
        d = self.reduce_buckets(self.generate_buckets(precision), number_buckets)
        keys = sorted(d.keys())
        for key in keys:
            with open(f_name + "_" + str(key),"w") as output_file:
                for element in d[key]:
                    output_file.write(zrc_path + element.id + seg_suffix + "\n")

def main(args):
    matrices_path = glob.glob(utils.folder(args.matrices_folder) + "*.txt")
    output_file = args.output_file
    ids_path = None
    if args.ids_path:
        ids_path = utils.folder(args.ids_path)

    c = Corpus(matrices_path, args.target, ids_path)

    if args.output_folder:
        output_folder = utils.folder(args.output_folder)
        c.write_invidual_files(output_folder)

    #c.write_summary(output_file + ".summary")
    #c.write_buckets(output_file + ".classes")
    #c.write_buckets(output_file + ".classes.verbose", verbose=True)
    if ids_path:
        c.write_zrc_buckets(utils.folder(args.segmentation_path), output_file, 10)
    
    #c.print_average()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--matrices-folder', type=str, nargs='?', help='soft-alignment probability matrices folder')
    parser.add_argument('--output-file', type=str, nargs='?', help='prefix name for the output name')
    parser.add_argument('target',type=bool, default=False, nargs='?', help='default considers that the source is to segment, include this option to segment the target')
    parser.add_argument('--output-folder', type=str, nargs='?', help='folder for storing individual files')
    parser.add_argument('--ids-path', type=str, nargs='?', help='Path for (train,dev).ids')
    parser.add_argument('--segmentation-path', type=str, nargs='?', help='Path for ZRC segmentation')
    args = parser.parse_args()
    if not (args.matrices_folder and args.output_file):
        parser.print_help()
        sys.exit(1)
    main(args)