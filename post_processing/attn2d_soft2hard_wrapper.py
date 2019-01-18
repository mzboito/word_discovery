import sys, os
import argparse
import soft2hard
from utils import generate_attn2d_folders


def check_root(root_directory):
    try:
        os.stat(root_directory)
    except:
        os.makedirs(root_directory)

def wrapper(args):
    if args.output_file:
        out_prefix = args.output_file
    
    folders = generate_attn2d_folders(int(args.layers))
   
    for folder in folders:
        if not args.output_file:
            output_folder = os.path.join(args.output_root_folder, folder)
            check_root(output_folder)
            args.output_folder = output_folder

        else:
            args.output_file = "_".join([folder,out_prefix])

        input_path = os.path.join(args.input_root_folder, folder) + "/"
        args.matrices_prefix = input_path
        args.pervasive = True
        #print(args.output_file, args.matrices_prefix)
        soft2hard.run(args)
                
                
if __name__ == "__main__":
    parser = soft2hard.get_soft2hard_parser()
    parser.add_argument('--input-root-folder', type=str, nargs='?', help='root directory for the attention folders')
    parser.add_argument('--layers', type=str, nargs='?', help='number of layers')
    parser.add_argument('--output-root-folder', type=str, nargs='?', help='root folder for storing the attention matrices')
    args = parser.parse_args()
    if len(sys.argv) < 3 or (not args.input_root_folder and not args.layers):
        parser.print_help()
        sys.exit(1)
    wrapper(args)