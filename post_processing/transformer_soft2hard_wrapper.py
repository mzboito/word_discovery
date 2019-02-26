import sys, os
import argparse
import soft2hard
from utils import generate_heads, transformer_decoder


def check_root(root_directory):
    try:
        os.stat(root_directory)
    except:
        os.makedirs(root_directory)

def wrapper(args):
    if args.output_file:
        out_prefix = args.output_file

    heads = generate_heads(int(args.heads), args.avg)
    for coder in transformer_decoder.keys():
        for layer in range(1,int(args.layers)+1):
            for attention_type in transformer_decoder[coder]:
                leaf = "/".join([coder, str(layer), attention_type])
                for head in heads:
                    if not args.output_file:
                        check_root(args.output_root_folder)
                        output_folder = "/".join([args.output_root_folder, "layer"+str(layer), head])
                        check_root(output_folder)
                        args.output_folder = output_folder
                    else:
                        args.output_file = args.dir +  "/" + "_".join(["layer"+str(layer),head,out_prefix]) if args.dir else "_".join(["layer"+str(layer),head,out_prefix])
                        print(args.output_file)
                    input_path = "/".join([args.input_root_folder, leaf]) + "/" + "*_" + head # + prefix + "*_" + head
                    args.matrices_prefix = input_path
                    args.transformer = True
                    #print(args.output_folder, args.matrices_prefix)
                    soft2hard.run(args)
                
                
if __name__ == "__main__":
    parser = soft2hard.get_soft2hard_parser()
    parser.add_argument('--input-root-folder', type=str, nargs='?', help='root directory for the attention folders')
    parser.add_argument('--heads', type=str, nargs='?', help='number of heads')
    parser.add_argument('--layers', type=str, nargs='?', help='number of layers')
    parser.add_argument('--output-root-folder', type=str, nargs='?', help='root folder for storing the attention matrices')
    parser.add_argument('--dir', type=str, nargs='?', help='segmentation\'s output file')
    parser.add_argument('avg', action="store_true", default=False, help='adds average matrices segmentation per layer')
    args = parser.parse_args()
    if len(sys.argv) < 3 or (not args.input_root_folder and not args.heads and not args.layers):
        parser.print_help()
        sys.exit(1)
    wrapper(args)
