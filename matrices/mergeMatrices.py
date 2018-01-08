## input: [1] path to the folder where are the rand folders; [2] list of ".lab" files; [3] output folder path

import sys
import codecs
import glob

def read_matrix(path):
	return [line.strip("\n").split("\t") for line in codecs.open(path,"r","UTF-8")]

def find_matrices(path_folders, folders, id):
    matrices = []
    for folder in folders:
        matrix_file = glob.glob(path_folders + folder + "att_model/*."+str(id)+".txt")
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

def load_files(path_folders, folders, file_list_name):
	d_list = dict(zip([],[]))
	for folder in folders:
		count = 1
		#print folder, folder[-2]
		d_list[folder] = []
		#print file_list_name, file_list_name.replace(folders[0],folder), folders[0], folder
		with open(path_folders + folder + file_list_name.replace(folders[0][:-1],folder[:-1]), "r") as inputFile:
			d_list[folder].append([inputFile.readline().strip(), count])
			count +=1
	return d_list

def main():
	path_folders = sys.argv[1]
	list_name = sys.argv[2]#files_list = [line.strip("\n") for line in open(sys.argv[2],"r")]
	output_folder = sys.argv[3]
	rand_num = int(sys.argv[4])
	folders = []#folders = ["rand1/", "rand2/", "rand3/", "rand4/", "rand5/"]
	for i in range(1,rand_num+1):
		folders.append("rand"+str(i)+"/")
	print folders
	d_list = load_files(path_folders, folders, list_name)
	print len(d_list)
	size = 5130#len(files_list)
	for i in range(0, size):

		#load the list files with indexes
		#get matrices i (send the generated dictionary to be able to find them)
		#avg matrices
		#write output

		#matrices = find_matrices(path_folders, folders, i+1)
        #avg_matrix = merge_matrices(matrices)
        #f = files_list[i]
        #write_output(output_folder + f, avg_matrix)


if __name__ == '__main__':
	main()
