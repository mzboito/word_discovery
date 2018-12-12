import sys, os
import argparse
import soft2hard
#coders = {"TransformerEncoder":["SelfAttention"], "TransformerDecoder":["SelfAttention", "EncoderDecoderAttention"]}

coders = {"TransformerDecoder":["EncoderDecoderAttention"]}

def check_root(root_directory):
    try:
        os.stat(root_directory)
    except:
        os.makedirs(root_directory)

def generate_heads(number):
    return ["head"+str(i+1) for i in range(number)] + ["avg"]

def wrapper(args):
    if args.matrices_prefix:
        prefix = args.matrices_prefix
    else:
        prefix = ""
    if args.output_file:
        out_prefix = args.output_file

    heads = generate_heads(int(args.heads))
    for coder in coders.keys():
        for layer in range(1,int(args.layers)+1):
            for attention_type in coders[coder]:
                leaf = "/".join([coder, str(layer), attention_type])
                for head in heads:
                    if not args.output_file:
                        check_root(args.output_root_folder)
                        output_folder = "/".join([args.output_root_folder, str(layer)])
                        check_root(output_folder)
                        args.output_folder = output_folder
                    else:
                        args.output_file = "_".join(["layer"+str(layer),head,out_prefix])
                    input_path = "/".join([args.input_root_folder, leaf]) + "/" + prefix + "*_" + head
                    args.matrices_prefix = input_path
                    args.transformer = True
                    #print(args.output_folder, args.matrices_prefix)
                    soft2hard.soft2hard(args)
                
                
if __name__ == "__main__":
    parser = soft2hard.get_soft2hard_parser()
    parser.add_argument('--input-root-folder', type=str, nargs='?', help='root directory for the attention folders')
    parser.add_argument('--heads', type=str, nargs='?', help='number of heads')
    parser.add_argument('--layers', type=str, nargs='?', help='number of layers')
    parser.add_argument('--output-root-folder', type=str, nargs='?', help='root folder for storing the attention matrices')
    args = parser.parse_args()
    if len(sys.argv) < 3 or (not args.input_root_folder and not args.heads and not args.layers):
        parser.print_help()
        sys.exit(1)
    wrapper(args)