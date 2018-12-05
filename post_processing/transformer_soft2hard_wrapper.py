import sys, os
import argparse
import soft2hard
coders = {"TransformerEncoder":["SelfAttention"], "TransformerDecoder":["SelfAttention", "EncoderDecoderAttention"]}
def check_root(root_directory):
    try:
        os.stat(root_directory)
    except:
        os.makedirs(root_directory)

def wrapper(args):
    check_root(args.output_root_folder)
    if args.matrices_prefix:
        prefix = args.matrices_prefix
    else:
        prefix = ""
    
    for coder in coders.keys():
        leaf = coder
        check_root("/".join([args.output_root_folder, leaf]))
        for layer in range(int(args.layers)):
            leaf = coder + "/" + str(layer+1)
            check_root("/".join([args.output_root_folder, leaf]))
            for attention_type in coders[coder]:
                leaf = "/".join([coder, str(layer+1), attention_type])
                output_folder = "/".join([args.output_root_folder, leaf])
                check_root(output_folder)
                args.output_folder = output_folder
                for head in range(int(args.heads)):
                    input_path = "/".join([args.input_root_folder, leaf]) + "/" + prefix + "*_head" + str(head)
                    args.matrices_prefix = input_path
                    #print(args.matrices_prefix, args.output_folder)
                    soft2hard.soft2hard(args)
                
if __name__ == "__main__":
    parser = soft2hard.get_soft2hard_parser()
    parser.add_argument('--input-root-folder', type=str, nargs='?', help='root directory for the attention folders')
    parser.add_argument('--heads', type=str, nargs='?', help='number of heads')
    parser.add_argument('--layers', type=str, nargs='?', help='number of layers')
    parser.add_argument('--output-root-folder', type=str, nargs='?', help='root folder for storing the attention matrices')
    args = parser.parse_args()
    if len(sys.argv) < 3 or not args.input_root_folder:
        parser.print_help()
        sys.exit(1)
    wrapper(args)