import sys, glob
import argparse
from entropy_gen import get_entropy_args, BaseMatrix, Corpus, Matrix
from utils import generate_heads, folder, transformer_decoder
from multiprocessing import Process

class MultiHead_Matrix():
    def __init__(self, matrices_root, layers, heads, id_matrix, target=True, segmentation=None):
        self.index = id_matrix
        self.matrices = []
        self.filepath = []
        for layer in range(1,(layers+1)):
            for head in heads:
                matrix_path = MultiHead_Matrix.transformer_path(matrices_root, layer, head).replace("/*_", "/" + str(id_matrix) + "_").replace("*",".txt")
                self.matrices += [BaseMatrix(matrix_path, target, segmentation)]
                self.filepath += [matrix_path]
        self.min = self.get_min_entropy()
    
    def get_min_entropy(self):
        entropy = self.matrices[0].average_entropy()
        path = self.matrices[0].filepath
        for m in self.matrices:
            m_entropy = m.average_entropy()
            if m_entropy < entropy:
                entropy = m_entropy
                path = m.filepath
        return (entropy, path)

    @staticmethod
    def transformer_path(matrices_root, layer, head):
        return "/".join([matrices_root, "TransformerDecoder", str(layer), "EncoderDecoderAttention"]) + "/*_" + head + "*"

class Multi_entropy_selector():
    def __init__(self, matrices_root, layers, heads, size, target=True):
        self.matrices = []
        for i in range(1,(size+1)): 
            self.matrices += [MultiHead_Matrix(matrices_root, layers,heads, str(i), target)]

    def wrapper(self):
        return [m.get_min_entropy() for m in self.matrices]
 
class Single_entropy_selector():
    def __init__(self, matrices_root, layers, heads, target=True):
        self.matrices_root = matrices_root
        self.layers_entropy = dict()
        for layer in range(1,int(args.layers)+1):
            heads_entropy = []
            for head in heads:
                matrices_path = glob.glob(MultiHead_Matrix.transformer_path(matrices_root, layer, head))
                c = Corpus(matrices_path, target)
                heads_entropy.append(c.get_average())
            print(layer, heads_entropy)
            self.layers_entropy[layer] = heads_entropy
        
    def wrapper(self, size=None):
        min_entropy = -1
        best_head = -1
        best_layer = 0
        for layer in self.layers_entropy.keys():
            heads_length = len(self.layers_entropy[layer])
            for i in range(heads_length):
                value = self.layers_entropy[layer][i]
                if value < min_entropy or min_entropy == -1:
                    min_entropy = value
                    best_head = i + 1
                    best_layer = layer

        return min_entropy, self.build_path(best_layer, best_head, size)
    
    def build_path(self, layer, head, size=None):
        #print(self.matrices_root, layer, "head"+(head+1))
        path = MultiHead_Matrix.transformer_path(self.matrices_root, layer, "head"+ str(head))[:-1] + ".txt"
        if size:
            return [path.replace("/*_", "/"+ str(i) + "_") for i in range(1,(size+1))]
        else:
            return [path]


class Output_writer():
    @staticmethod
    def write_single(path, f_name):
        with open(f_name,"w") as output_file:
            output_file.write(path + "\n")
        
    def write_multiples(paths, f_name):
        with open(f_name,"w") as output_file:
            for path in paths:
                output_file.write(path + "\n")
    
    def write_summary(heads, wrapper, f_name):
        with open(f_name,"w") as output_file:
            output_file.write("\t".join([""] + heads) + "\n")
            for layer in wrapper.layers_entropy.keys():
                entropy_values = [str(element) for element in wrapper.layers_entropy[layer]]
                output_file.write("\t".join([str(layer)] + entropy_values) + "\n")

def process_multi(args, heads):
    corpus = Multi_entropy_selector(args.input_root_folder, args.layers, heads, args.size)
    info = corpus.wrapper()
    average = sum([element[0] for element in info]) / len(info)
    paths = [element[1] for element in info]
    print(average)
    Output_writer.write_multiples(paths, args.output_dir +  "/multihead_entropy_list")
    Output_writer.write_single(str(average), args.output_dir +  "/multihead_avg_entropy")

def process_single(args, heads):
    corpus = Single_entropy_selector(args.input_root_folder, args.layers, heads)
    value, path = corpus.wrapper(args.size)
    print(value)#, path)
    Output_writer.write_multiples(path, args.output_dir + "/singlehead_entropy_list")
    Output_writer.write_summary(heads, corpus, args.output_dir + "/entropy_summary")

def wrapper(args):
    print(args)
    args.avg = False
    heads = generate_heads(args.heads, args.avg)
    print(heads)
    
    if args.multi:
        process_multi(args, heads)
        #p = Process(target=process_multi, args=(args, heads))
        #p.start()
    
    if args.single:
        process_single(args, heads)
        #p = Process(target=process_single, args=(args, heads))
        #p.start()

    #p.join()

if __name__ == "__main__":
    parser = get_entropy_args(argparse.ArgumentParser())
    parser.add_argument('--input-root-folder', type=str, nargs='?', help='root directory for the attention folders')
    parser.add_argument('--heads', type=int, nargs='?', default=2, help='number of heads')
    parser.add_argument('--layers', type=int, nargs='?', default=3, help='number of layers')
    parser.add_argument('--size', type=int, nargs='?', help='number of elements in the test set')
    parser.add_argument('--output-dir', type=str, nargs='?', help='output folder for the filtered matrices')
    #parser.add_argument('--log', type=str, nargs='?', help='name for the output log file')
    parser.add_argument('avg', action='store_true', default=False, help='includes entropy for avg matrix per layer')
    parser.add_argument('--multi', action='store_true',default=False, help='does the selection per matrix')
    parser.add_argument('--single', action='store_true',default=False, help='does the selection per general average')
    args = parser.parse_args()
    if not (args.input_root_folder):
        parser.print_help()
        sys.exit(1)
    wrapper(args)

    
