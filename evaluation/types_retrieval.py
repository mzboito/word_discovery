import sys, glob
import argparse

N_set = ["50", "200", "500", "1000", "2000", "3000", "4000","5000"]

def read_set(f_file):
    dictionary = dict()
    with open(f_file) as base_file:
        for line in base_file:
            key = line.strip().split("\t")[-1]
            token = line.split("\t")[1]
            if key not in dictionary: #!!
                dictionary[key] = [token]
            elif token not in dictionary[key]:
                dictionary[key].append(token)
    return dictionary
            
def read_N(f_file):
    mono = dict()
    bi = dict()
    mono["base_file"] = f_file
    for dictionary in [mono]:
        for n_set in N_set:
            dictionary[n_set] = read_set(dictionary["base_file"].replace(".cleaned","."+ n_set +".cleaned"))
        dictionary["all"] = read_set(dictionary["base_file"])
    del mono["base_file"]
    return mono

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
    p = precision(dictionary)
    r = recall(dictionary, vocabulary)
    return (p, r, fscore(p, r))


def evaluate_sets(dictionary, vocabulary):
    output_dict = dict()
    for key in dictionary.keys():
        output_dict[key] = evaluate(dictionary[key], vocabulary)
    return output_dict

def load_vocab(vocab_file):
    return [line.strip().split("\t")[0] for line in open(vocab_file,"r")]

def write_output(dictionary, f_path):
    with open(f_path, "w") as output_file:
        output_file.write("\t".join(["set","precision","recall","fscore"]) + "\n")
        for key in dictionary:
            output_file.write("\t".join([key, str((dictionary[key][0]*100)), str((dictionary[key][1]*100)), str(((dictionary[key][2])*100) )]) + "\n")

def read_input(f_path, gold):
    dictionary = { "1":[], "0":[] }
    with open(f_path, "r") as input_file:
        for line in input_file:
            line = line.strip()
            if line in gold:
                dictionary["1"].append(line)
            else:
                dictionary["0"].append(line)
    return dictionary


def eval(args):
    vocabulary = load_vocab(args.vocab)
    if args.all:
        dictionary = read_input(args.input, vocabulary)
        output_info = evaluate(dictionary, vocabulary)
        output_info = {"all": output_info}
    elif args.ranking:
        dictionary = read_N(args.input)
        output_info = evaluate_sets(dictionary, vocabulary)
    write_output(output_info, args.output)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--all', default=False, action='store_true', help='evaluates only one file')
    parser.add_argument('--ranking', default=False, action='store_true', help='evaluates N sub-groups')
    parser.add_argument('--vocab', type=str, nargs='?', help='gold vocabulary')
    parser.add_argument('--input', type=str, nargs='?', help='generated vocabulary')
    parser.add_argument('--output', type=str, nargs='?', help='output file name')
    args = parser.parse_args()
    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(1)
    eval(args)
