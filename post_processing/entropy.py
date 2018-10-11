import codecs
import sys
import glob
from math import log, e
import numpy as np


def read_matrix(path):
    return [line.strip("\n").split("\t") for line in codecs.open(path,"r","utf-8")]

def KL_divergence(P,Q): #P true Q observed
    assert len(P) == len(Q)
    return np.sum(P*np.log(P/Q))

def generate_flat_distribution(size):
    distribution = np.empty(shape=(0,))
    value = 1.0/size
    for i in range(size):
        distribution = np.append(distribution, value)
    return distribution

def generate_one_peak_distribution(size):
    distribution = np.empty(shape=(0,))
    distribution = np.append(distribution, 0.99)
    value = 0.1/(size-1)
    for i in range(1,size):
        distribution = np.append(distribution, value)
    return distribution

def generate_two_peak_distribution(size):
    distribution = np.empty(shape=(0,))
    peak = 0.99/2
    distribution = np.append(distribution, peak)
    value = 0.1/(size-2)
    for i in range(1,(size-2)):
        distribution = np.append(distribution, value)
    distribution = np.append(distribution, peak)
    return distribution


def write_result(output_path, id, avg_kl):
    with codecs.open(output_path,"a","utf-8") as output_file:
        output_file.write(id+"\t" + str(avg_kl) + "\n")


def format_distribution(line):
    line = line[1:] #remove phone token
    new_dist = np.empty(shape=(0,))
    for i in range(len(line)):
        new_dist = np.append(new_dist,float(line[i]))
    #print(np.sum(new_dist))
    return new_dist

def test(matrix):
    flat_dist = generate_flat_distribution(len(matrix[0])-1)
    peak_dist = generate_one_peak_distribution(len(matrix[0])-1)
    two_peak_dist = generate_two_peak_distribution(len(matrix[0])-1)
    print(flat_dist)
    print("entropy: " + str(entropy(flat_dist,2)))
    print(peak_dist)
    print("entropy: " + str(entropy(peak_dist,2)))
    print(two_peak_dist)
    print("entropy: " + str(entropy(two_peak_dist,2)))

def entropy(P, base=None):
    n_classes = len(P)
    if n_classes <= 1:
        return 0
    ent = 0.
    base = e if base is None else base
    for i in P:
        ent -= i * log(i, base)
    return ent / log(n_classes,base)

def main():
    matrices_folder = sys.argv[1]
    output_file = sys.argv[2]
    output_folder = sys.argv[3] if sys.argv[3][-1] == '/' else sys.argv[3] + '/'
    matrices_path = glob.glob(matrices_folder + "*.txt")
    for matrix_path in matrices_path:
        matrix = read_matrix(matrix_path)
        acc = 0.0
        with codecs.open(output_folder + matrix_path.split("/")[-1],"w","utf-8") as individual_file:
            for i in range(1,len(matrix)): #for each line (first one is the list of words)
                phone_dist = format_distribution(matrix[i])
                ent = entropy(phone_dist)
                individual_file.write(str(ent))
                individual_file.write("\n")
                acc += ent
            avg_kl = acc / (len(matrix)-1)
        write_result(output_file, matrix_path, avg_kl)


if __name__ == '__main__':
    main()




