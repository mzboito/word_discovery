import sys, glob
import argparse
from entropy_gen import get_entropy_args, Corpus
from utils import generate_heads, folder, transformer_decoder

def write_log(f_path, dictionary, header):
    with open(f_path, "w") as output_file:
        output_file.write("\t" + "\t".join(header) + "\n")
        for key in dictionary.keys():
            str_values = [str(value) for value in dictionary[key]]
            output_file.write("\t". join([str(key)] + str_values) + "\n")

def wrapper(args):
    heads = generate_heads(int(args.heads), args.avg)
    layers_entropy = dict()
    for coder in transformer_decoder.keys():
        for layer in range(1,int(args.layers)+1):
            for attention_type in transformer_decoder[coder]:
                path = "/".join([args.input_root_folder, coder, str(layer), attention_type]) + "/"
                heads_entropy = []
                for head in heads:
                    matrices_path = glob.glob(path +"*"+ head +".txt")
                    ids_path = None
                    if args.ids_path:
                        ids_path = folder(args.ids_path)
                    c = Corpus(matrices_path, args.target, ids_path)
                    if args.output_folder:
                        output_folder = folder(args.output_folder)
                        c.write_invidual_files(output_folder)
                    if args.output_file:
                        c.write_summary(args.output_file + "_".join(["layer"+str(layer), head]) +  ".summary")
                    heads_entropy.append(c.get_average())
                layers_entropy[layer] = heads_entropy
        if args.log:
            write_log(args.log, layers_entropy, heads)
        


if __name__ == "__main__":
    parser = get_entropy_args(argparse.ArgumentParser())
    parser.add_argument('--input-root-folder', type=str, nargs='?', help='root directory for the attention folders')
    parser.add_argument('--heads', type=str, nargs='?', help='number of heads')
    parser.add_argument('--layers', type=str, nargs='?', help='number of layers')
    parser.add_argument('--log', type=str, nargs='?', help='name for the output log file')
    parser.add_argument('avg', action='store_true',default=False, help='includes entropy for avg matrix per layer')
    args = parser.parse_args()
    if not (args.input_root_folder):
        parser.print_help()
        sys.exit(1)
    wrapper(args)

    