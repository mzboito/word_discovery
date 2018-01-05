import sys
import codecs
import glob

def read_matrix(path):
	return [line.strip("\n").split("\t") for line in codecs.open(path,"r","UTF-8")]

def find_matrices(path_folders, folders, id):
    matrices = []
    for folder in folders:
        matrix_file = glob.glob(path_folders + folder + "/*."+str(id)+".txt")
        matrix = read_matrix(matrix_file[0])
        matrices.append(matrix)
    if len(matrices) != len(folders):
        print "carefull, we are missing some matrices..."
    return matrices

def merge_matrices(matrices_list):
    num_lines = len(matrices_list[0])
    num_columns = len(matrices_list[0][0]) + 1
    num_matrices = len(matrices_list)
    output = [[0 for i in xrange(num_columns)] for j in xrange(num_lines)]
    output[0] = matrices_list[0][0]
    for line in range(1, num_lines):
        output[line][0] = matrices_list[0][line][0]
        for column in range(1, num_columns):
            for i in range(0, num_matrices):
                if len(matrices_list[i][line]) > 1:
                    output[line][column] += float(matrices_list[i][line][column])
            output[line][column] = str(output[line][column] / num_matrices)
    return output

def write_output(path, matrix):
    output_path = path.replace(".lab", ".attmat")
    print output_path
    with codecs.open(output_path, "w", "UTF-8") as outputFile:
        for line in matrix:
            print line, "\t".join(line)
            try:
                outputFile.write("\t".join(line) + "\n")
            except TypeError:
                pass

def main():
    path_folders = sys.argv[1]
    folders = ["rand1", "rand2", "rand3"]#, "rand4", "rand5"]
    files_list = [line.strip("\n") for line in open(sys.argv[2],"r")]
    output_folder = sys.argv[3]
    size = len(files_list)
    for i in range(0, size):
        matrices = find_matrices(path_folders, folders, i+1)
        avg_matrix = merge_matrices(matrices)
        f = files_list[i]
        write_output(output_folder + f, avg_matrix)


if __name__ == '__main__':
    main()
