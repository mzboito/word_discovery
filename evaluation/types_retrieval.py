import sys, glob

N_set = ["50", "200", "500", "1000", "2000", "3000", "5000"]

def read_set(f_file):
    dictionary = dict()
    with open(f_file) as base_file:
        for line in base_file:
            key = line.strip().split("\t")[-1]
            token = line.split("\t")[1]
            if key not in dictionary:
                dictionary[key] = [token]
            elif token not in dictionary[key]:
                dictionary[key].append(token)

    return dictionary
            
def read_input(f_file):
    mono = dict()
    bi = dict()
    mono["base_file"] = f_file
    for dictionary in [mono]:
        for n_set in N_set:
            dictionary[n_set] = read_set(dictionary["base_file"].replace(".cleaned","."+ n_set +".cleaned"))
        dictionary["all"] = read_set(dictionary["base_file"])
    del mono["base_file"]
    return mono

def read_vocab(f_path):
    types = []
    labs_path = glob.glob(f_path + "/*")
    for f_path in labs_path:
        tokens = [line.strip().split(" ")[2] for line in open(f_path, "r")] 
        for i in range(len(tokens)):
            if tokens[i] != "SIL" and tokens[i] not in types:
                types.append(tokens[i])
    return types

def precision(dictionary):
    correct = len(dictionary["1"])
    total_discovered = sum([len(dictionary[key]) for key in dictionary.keys()]) * 1.0
    return correct / total_discovered

def recall(dictionary, vocabulary):
    correct = len(dictionary["1"])
    length_vocabulary = len(vocabulary)*1.0
    return correct / length_vocabulary

def fscore(p, r):
    return 2.0 * ((r*p) / (r+p))

def evaluate(dictionary, vocabulary):
    output_dict = dict()
    for key in dictionary.keys():
        p = precision(dictionary[key])
        r = recall(dictionary[key], vocabulary)
        output_dict[key] = (p, r, fscore(p, r))
    return output_dict

def write_output(dictionary, f_path):
    with open(f_path, "w") as output_file:
        output_file.write("\t".join(["set","precision","recall","fscore"]) + "\n")
        for key in dictionary:
            output_file.write("\t".join([key, str((dictionary[key][0]*100)), str((dictionary[key][1]*100)), str(((dictionary[key][2])*100) )]) + "\n")

def eval():
    base_file = sys.argv[1] #e.g. transformer_bi_mboshi_5k.cleaned.csv
    vocab_file = sys.argv[2]
    output_file = sys.argv[3]


    mono = read_input(base_file)

    vocabulary = read_vocab(vocab_file)

    mono_output = evaluate(mono, vocabulary)
    write_output(mono_output, output_file)
    



if __name__ == "__main__":
    eval()