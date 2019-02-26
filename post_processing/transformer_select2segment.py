import sys, glob
import argparse
from entropy_gen import get_entropy_args, Corpus
from utils import generate_heads, folder, transformer_decoder

def get_entropy(args):
    heads = generate_heads(int(args.heads), args.avg)
    #print(heads)
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
                layers_entropy[layer] = [heads_entropy, path]
    return layers_entropy

def get_min(layers_entropy):
    min_entropy = -1
    best_path = ''
    head = -1
    for layer in layers_entropy.keys():
        entropy_list = layers_entropy[layer][0]
        path = layers_entropy[layer][1]
        for i in range(len(entropy_list)):
            #print(i)
            value = entropy_list[i]
            #print(value)
            if value < min_entropy or min_entropy == -1:
                min_entropy = value
                best_path = path
                head = i +1
    return min_entropy, (best_path +"*"+ str(head) +".txt")


def wrapper(args):
    print(args)
    args.avg = False
    layers_entropy = get_entropy(args)
    #print(layers_entropy)
    #print(get_min(layers_entropy))
    value, path = get_min(layers_entropy)
    final_path = path #"/".join([args.input_root_folder, path])
    with open("best_entropy","w") as output_file:
        output_file.write(final_path + "\n")

        
        


if __name__ == "__main__":
    parser = get_entropy_args(argparse.ArgumentParser())
    parser.add_argument('--input-root-folder', type=str, nargs='?', help='root directory for the attention folders')
    parser.add_argument('--heads', type=str, nargs='?', help='number of heads')
    parser.add_argument('--layers', type=str, nargs='?', help='number of layers')
    parser.add_argument('--output-dir', type=str, nargs='?', help='output folder for the filtered matrices')
    #parser.add_argument('--log', type=str, nargs='?', help='name for the output log file')
    parser.add_argument('avg', action='store_true',default=False, help='includes entropy for avg matrix per layer')
    #parser.add_argument('single', action='store_true',default=False, help='does the filtering per matrix')
    args = parser.parse_args()
    if not (args.input_root_folder):
        parser.print_help()
        sys.exit(1)
    wrapper(args)

    
