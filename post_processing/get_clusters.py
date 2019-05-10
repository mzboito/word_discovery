import sys, codecs, utils

def read_table(f_path):
    dictionary = dict()
    with codecs.open(f_path,"r","utf-8") as input_table: # file, phonemes, translation, entropy
        for line in input_table:
            line = line.strip().split("\t")
            key = line[2]
            word = line[1]
            entropy = float(line[3])
            freq =  1
            #if key != "</S>":
            if key not in dictionary:
                dictionary[key] = dict()
                dictionary[key][word] = [entropy, freq]
            elif word not in dictionary[key]:
                dictionary[key][word] = [entropy, freq]
            else:
                entropy = (entropy + dictionary[key][word][0]) / 2
                freq += dictionary[key][word][1]
                dictionary[key][word] = [entropy, freq]
    return dictionary

def cluster_ane(dictionary):
    return (sum([float(dictionary[key][0]) for key in dictionary.keys()])) / (len(dictionary.keys())*1.0)

def sort_dictionary(dictionary):
    tuples = list()
    for key in dictionary.keys():
        value = cluster_ane(dictionary[key])
        tuples.append( (key, value))
    tuples.sort(key=lambda x:x[1])
    return tuples

def write_clusters(table, keys, f_name):
    with codecs.open(f_name,"w","utf-8") as output_test:
        for key, ane in keys:
            output_test.write("\t".join([key, str(ane), str(len(table[key]))]) + "\n")
            for element in table[key]:
                str_elements = [element, str(table[key][element][0]), str(table[key][element][1])]
                output_test.write("\t".join(str_elements) + "\n")
            output_test.write("\n")


def write_lexicon(keys, f_name):
    with codecs.open(f_name,"w","utf-8") as output_file:
        for key, value in keys:
            output_file.write("\t".join([key, str(value)]) + "\n")

def process():
    #generate clusters
    table = read_table(sys.argv[1])
    clusters_f = sys.argv[2]
    
    #sort per cluster ANE
    sorted_keys = sort_dictionary(table)

    #write clusters
    write_clusters(table, sorted_keys, clusters_f+".csv") 
    write_lexicon(sorted_keys, clusters_f+".lst")



if __name__ == "__main__":
    process()