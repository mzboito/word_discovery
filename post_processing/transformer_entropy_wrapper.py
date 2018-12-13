import sys, glob
import argparse
from entropy_gen import get_entropy_args, Corpus
from utils import generate_heads, folder

coders = {"TransformerDecoder":["EncoderDecoderAttention"]}

def wrapper(args):
    heads = generate_heads(int(args.heads))

    for coder in coders.keys():
        for layer in range(1,int(args.layers)+1):
            for attention_type in coders[coder]:
                path = "/".join([args.input_root_folder, coder, str(layer), attention_type]) + "/"
                for head in heads:
                    matrices_path = glob.glob(path +"*"+ head +".txt")
                    ids_path = None
                    if args.ids_path:
                        ids_path = folder(args.ids_path)
                    c = Corpus(matrices_path, args.target, ids_path)
                    if args.output_folder:
                        output_folder = folder(args.output_folder)
                        c.write_invidual_files(output_folder)
                    c.write_summary(args.output_file + "_".join(["layer"+str(layer), head]) +  ".summary")
                    print(layer, head)
                    c.print_average()


if __name__ == "__main__":
    parser = get_entropy_args(argparse.ArgumentParser())
    parser.add_argument('--input-root-folder', type=str, nargs='?', help='root directory for the attention folders')
    parser.add_argument('--heads', type=str, nargs='?', help='number of heads')
    parser.add_argument('--layers', type=str, nargs='?', help='number of layers')
    args = parser.parse_args()
    if not (args.input_root_folder and args.output_file):
        parser.print_help()
        sys.exit(1)
    wrapper(args)

    