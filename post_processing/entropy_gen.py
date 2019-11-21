import sys, utils
import codecs, glob, math
import Entropy
import numpy as np
from segment import segment_target
import soft2hard as s2h
import argparse


#### STUFF I'M LAZY TO TYPE ON THE COMMAND LINE
'''
seg_suffix = ".hs"
flag_id_none=False #just to avoid multiples print of the same information when the id crashes
'''

'''
1) generate matrices with entropy per line
2) generate average entropy per matrix
3) generate average and number of tokens per matrix
4) generate classes (entropy buckets) files listing the files inside and count 
'''


def get_entropy_args(parser):
    parser.add_argument('--matrices-folder', type=str, nargs='?', help='soft-alignment probability matrices folder')
    parser.add_argument('--output-file', type=str, nargs='?', help='prefix name for the output name')
    parser.add_argument('--dispersion', type=float, nargs='?', help='Dispersion degree for ANE penalization')
    #optional: ids path for labeling and output folder for individual results
    parser.add_argument('--ids-path', type=str, nargs='?', help='Path for (train,dev).ids')
    parser.add_argument('--buckets', default=False, action='store_true', help='folder for storing individual files')
    parser.add_argument('--output-folder', type=str, nargs='?', help='folder for storing individual files')
    #stuff for generating ZRC subsets
    parser.add_argument('--segmentation-path', type=str, nargs='?', help='Path for ZRC segmentation')
    parser.add_argument('--labs-path', type=str, nargs='?', help='Path for labs')
    
    return parser


class BaseMatrix():
    def __init__(self, filepath, target=True, segmentation=None, dispersion=0):
        self.filepath = filepath
        self.lines = utils.read_matrix_file(filepath)
        self.alignments = list()
        self.entropies, self.alignments = self.entropy(self.lines)
        self.dispersion = dispersion
        self.file_name = self.get_file_name(filepath)
        if segmentation: #segmentation only necessary when producing buckets
            self.tokens = segment_target(self.lines, target)[0].split(" ")
        else:
            self.tokens = list()

    @staticmethod
    def entropy(matrix):
        entropies = list()
        alignments = list()
        for i in range(1,len(matrix)): #for each line (first one is the list of words)
                phone_dist = Entropy.format_distribution(matrix[i])
                ent = Entropy.entropy(phone_dist)
                alignments.append(s2h.get_max_prob_col(i, matrix))
                entropies.append(ent)
        return entropies, set(alignments)

    def average_entropy(self):
        avg_entropy = sum(self.entropies) / (len(self.entropies)*1.0)
        #if self.dispersion > 0:
        coverage = 1 - (len(self.alignments)*1.0) / (len(self.lines[0]) - 1)
        return (((1 - self.dispersion) * avg_entropy) + (self.dispersion * coverage))
        #return avg_entropy

    def number_tokens(self):
        return len(self.tokens)
    
    def average_length(self):
        return sum([len(t) for t in self.tokens]) / len(self.tokens)
    
    def get_file_name(self, filepath):
        return filepath.split("/")[-1]

class Matrix(BaseMatrix):
    def __init__(self, filepath, target=True, segmentation=True, ids_dictionary=None, dispersion=0):
        super().__init__(filepath, target=target, segmentation=segmentation, dispersion=dispersion)
        self.file_name = self.get_file_name(filepath)

        if ids_dictionary:
            try: #seq2seq
                self.index = int(self.file_name.split(".")[1])
            except ValueError: #pervasive case
                try:
                    self.index = int(self.file_name.split(".")[0].split("_")[0]) 
                except: #en-fr ids
                    self.index = int(self.file_name.split(".")[0].split("_")[1])      
            try:
                self.id = ids_dictionary[self.index-1]
            except KeyError:
                self.id = None
                global flag_id_none
                if not flag_id_none:
                    print("Problem with id file, setting id to None")
                    flag_id_none=True

class BaseCorpus():
    def __init__(self, matrices_path, matrix_class, target=True, ids_dictionary=None, dispersion=0):
        self.matrices = []
        self.matrix_class = matrix_class
        for matrix_path in matrices_path:
            self.matrices.append(matrix_class(matrix_path, target=target, ids_dictionary=ids_dictionary, dispersion=dispersion))

    def get_average(self):
        return self.average_from_group(self.matrices, self.matrix_class.average_entropy)

    def print_average(self):
        print(self.get_average())

    def average_from_group(self, m_list, function):
        acc = 0
        for m in m_list:
            acc += function(m)
        return acc / len(m_list)

class Corpus(BaseCorpus):
    def __init__(self, matrices_path, target=True, ids_path=None, dispersion=0):
        ids_dictionary = self.read_ids(ids_path)
        super().__init__(matrices_path, Matrix, target, ids_dictionary, dispersion)
    
    def read_ids(self, ids_path):
        if ids_path:
            ids_dict = dict()
            count = 1
            with open(ids_path,"r") as input_ids:
                for line in input_ids:
                    ids_dict[count] = line.strip()
                    count +=1
            return ids_dict
        return None

class Buckets():
    def __init__(self, precision=2, number_buckets=10):
        self.precision = precision
        self.buckets = dict()
        self.number_buckets = number_buckets

    def generate_buckets(self, corpus):
        for m in corpus.matrices:
            avg = round(m.average_entropy(), self.precision)
            if avg in self.buckets:
                self.buckets[avg].append(m)
            else:
                self.buckets[avg] = [m]

    def reduce_buckets(self, corpus):
        bucket = 1
        new_buckets = dict({bucket:[]})
        size_buckets = len(corpus.matrices) / self.number_buckets
        keys = sorted(self.buckets.keys())
        for key in keys:
            for element in self.buckets[key]:
                if len(new_buckets[bucket]) < size_buckets or bucket == size_buckets:
                    new_buckets[bucket].append(element)
                else:
                    bucket+=1
                    new_buckets[bucket] = [element]
        self.buckets = new_buckets
        #return new_buckets

class Output_writer():
    @staticmethod
    def write_invidual_files(corpus, folder):
        for m in corpus.matrices:
            write_matrix(folder, m)
    
    @staticmethod
    def write_matrix(folder, matrix):
        with codecs.open(folder + matrix.file_name, "w","utf-8") as output_file:
            output_file.write("\t".join(matrix.lines[0] + ["Entropy"]) + "\n")
            for i in range(1,len(matrix.lines)):
                output_file.write("\t".join(matrix.lines[i] + [str(matrix.entropies[i-1])]) + "\n")

    @staticmethod
    def write_summary(corpus, f_name):
        with open(f_name, "w") as output_file:
            output_file.write("{}\t{}\t{}\t{}\n".format("id", "avg_entropy", "#tokens","avg_token_length"))
            for m in corpus.matrices:
                output_file.write("%s\t%.2f\t%.2f\t%.2f\n" %(m.file_name, m.average_entropy(), m.number_tokens(), m.average_length()))

    @staticmethod
    def write_sublab_file(f_name, m_list, labs_path):
        with open(f_name, "w") as output_file:
            for element in m_list:
                output_file.write(labs_path + element.id + "\n")
    
    @staticmethod
    def write_entropy(corpus, f_path):
        with open(f_path,"w") as output_file:
            output_file.write(str(corpus.get_average()) + "\n")

    @staticmethod
    def write_buckets(bucket_obj, f_name):
        for key in bucket_obj.buckets.keys():
            with open(f_name + "_" + str(key),"w") as output_bucket:
                for element in bucket_obj.buckets[key]:
                    output_bucket.write(element.filepath + "\n")
        
    @staticmethod
    def write_zrc_buckets(corpus, bucket_obj, zrc_path, labs_path, f_name):
        bucket_obj.generate_buckets(corpus)
        bucket_obj.reduce_buckets(corpus)
        d = bucket_obj.buckets
        keys = sorted(d.keys())
        summary = []
        for key in keys:
            name = f_name + "_" + str(key)
            with open(name,"w") as output_file:
                for element in d[key]:
                    output_file.write(zrc_path + element.id + seg_suffix + "\n")
            write_sublab_file(name + "_labs", d[key], labs_path)            
            summary.append([str(key), str(corpus.average_from_group(d[key], Matrix.average_entropy))])

        with open(f_name + ".summary", "w") as output_file:
            for element in summary:
                output_file.write("\t".join(element) + "\n")
    
    '''@staticmethod
    def write_buckets(f_name, corpus, bucket_obj, verbose=False):
        buckets.generate_buckets()
        d = bucket_obj.buckets
        keys = sorted(d.keys())
        with open(f_name, "w") as output_file:
            output_file.write("group\tmembers\ttoken\tlength\n")
            for key in keys:
                output_file.write("{}\t{}\t{}\t{}\n".format(key, len(d[key]), 
                    round(corpus.average_from_group(d[key], Matrix.number_tokens), bucket_obj.precision), round(corpus.average_from_group(d[key], Matrix.average_length), bucket_obj.precision)))
                if verbose:
                    for m in d[key]:
                        output_file.write("\t{}\t{}\n".format(m.file_name, m.average_entropy()))
                    output_file.write("\n")'''
    
def main(args):
    matrices_path = glob.glob(args.matrices_folder + "/*.txt")
    #print(len(matrices_path))

    
    c = Corpus(matrices_path, dispersion=args.dispersion)
    if args.output_folder:
        
        output_folder = utils.folder(args.output_folder)
        Output_writer.write_invidual_files(c,output_folder)

    if args.output_file:
        Output_writer.write_summary(c,args.output_file + ".summary")
        Output_writer.write_entropy(c,args.output_file)

    c.print_average()

    if args.buckets:
        b = Buckets(precision=1)
        b.generate_buckets(c)
        Output_writer.write_buckets(b, args.output_file)

    
    '''old bucket stuff
    if ids_path:
        #c.write_buckets(output_file + ".classes")
        #c.write_buckets(output_file + ".classes.verbose", verbose=True)
        c.write_zrc_buckets(utils.folder(args.segmentation_path), utils.folder(args.labs_path), args.output_file)
    ''' 

if __name__ == '__main__':
    parser = get_entropy_args(argparse.ArgumentParser())
    args = parser.parse_args()
    if not (args.matrices_folder):
        parser.print_help()
        sys.exit(1)
    main(args)
