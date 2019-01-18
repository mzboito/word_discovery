import sys, os, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from evaluation import evaluate, get_evaluation_parser
from post_processing.utils import generate_attn2d_folders

def wrapper(args):
    folders = generate_attn2d_folders(int(args.layers))
    for folder in folders:
            file_name = folder + "_" + args.suffix
            args.segmentation = file_name
            args.output = file_name.replace(args.suffix, "eval")
            evaluate(args)



if __name__ == "__main__":
    parser = get_evaluation_parser(argparse.ArgumentParser())
    parser.add_argument('--suffix', type=str, nargs='?', help='suffix of the segmentation')
    parser.add_argument('--layers', type=str, nargs='?', help='number of layers')
    args = parser.parse_args()
    if not args.layers:
        parser.print_help()
        sys.exit(1)
    wrapper(args)
