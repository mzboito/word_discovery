import sys, codecs, glob, argparse
from entropy_gen import Matrix
#from utils import write_output_matrix, read_matrix_file

def get_matrix_file(f_id, matrices_folder, pervasive, transformer):
	if pervasive:
		path_str = str(f_id) + ".txt"
	elif transformer:
		path_str = str(f_id) + "_*.txt"
	else:
		path_str =  ".".join(["*",str(f_id), "txt"])
	try:
		#print("/".join([matrices_folder, path_str]))
		matrix_file = glob.glob("/".join([matrices_folder, path_str]))[0]
		return matrix_file
	except IndexError:
		raise Exception("INVALID PATH. Root folder: " + matrices_folder + " file: " + path_str)

def get_index_from_file(files_dict, folder, f_name):
	for key in files_dict[folder].keys():
		if key == f_name:
			return files_dict[folder][key]
	raise Exception("PROBLEM GETTING ID FROM DICTIONARY:\nfile: " + f_name + " folder: " + folder)

def find_matrices(root_folder, folders, files_dict, file_name, dispersion):
	matrices = []
	for folder in folders:
		f_id = get_index_from_file(files_dict, folder, file_name)
		#print(f_id)
		path = "/".join([args.root_folder, folder, args.matrices_folder])
		matrix_file = get_matrix_file(f_id, path, args.pervasive, args.transformer)
		matrix = Matrix(matrix_file, dispersion=dispersion)
		#matrix = read_matrix_file(matrix_file)
		matrices.append(matrix)
	assert len(matrices) == len(folders), "COULD NOT READ ALL THE MATRICES FOR FILE: " + file_name
	'''size = len(matrices[0])
	for i in range(1, len(folders)):
		assert len(matrices[i]) == size, "PROBLEM WITH MATRIX SIZE: " + file_name'''
	return matrices

def get_file_from_index(files_dict, folder, f_id):
	for key in files_dict[folder].keys():
		if files_dict[folder][key] == f_id:
			return key
	raise Exception("PROBLEM GETTING KEY FROM DICTIONARY:\nid: " + str(f_id) + " folder: " + folder)

def read_ids_file(f_path):
	count = 1
	intern_dict = dict() #creates intern dict
	with open(f_path, "r") as input_file: #reads id file
		for line in input_file:
			intern_dict[line.strip()] = count #{id name, index}
			count += 1
	return intern_dict

def load_files(args):
	FILES_DICT = dict()
	folders = generate_folders(args.model_prefix, args.number)
	for folder in folders:
		FILES_DICT[folder] = list() #creates entry for folder
		file_name = args.ids_file
		FILES_DICT[folder] = read_ids_file(args.ids_file)
	return FILES_DICT

def generate_folders(prefix, number):
	return [prefix+str(i) for i in range(1, (number+1))]

'''def get_entropy(matrix, dispersion):
	entropies, sum_align = BaseMatrix.entropy(matrix)
	avg_entropy = sum(entropies) / (len(entropies)*1.0)
	if dispersion > 0:
		coverage = 1 - (len(sum_align)*1.0) / (len(matrix[0]) - 1)
		return (((1 - dispersion) * avg_entropy) + (dispersion * coverage))
	else:
		return avg_entropy '''

def get_min_entropy(matrices):
	min_e = matrices[0].average_entropy() #get_entropy(matrices[0])
	min_matrix = matrices[0]
	for i in range(1, len(matrices)):
		this_e = matrices[i].average_entropy() #get_entropy(matrices[i])
		if this_e < min_e:
			min_matrix = matrices[i]
			min_e = this_e
	print(min_e)
	return min_matrix

def write_output_matrix(path, matrix):
	with codecs.open(path, "w", "UTF-8") as outputFile:
		for line in matrix.lines:
			outputFile.write("\t".join(line) + "\n")

def wrapper(args):
	print(args)
	folders = generate_folders(args.model_prefix, args.number)
	FILES_DICT = load_files(args) #load files
	size = len(FILES_DICT[folders[-1]])

	for i in range(1, args.number):
		assert len(FILES_DICT[folders[i]]) == size, "PROBLEM READING THE LISTS (INDEX = " + str(i) + ")"

	for i in range(1, size+1):

		file_i = get_file_from_index(FILES_DICT, folders[0], i)
		matrices = find_matrices(args.root_folder, folders, FILES_DICT, file_i, args.dispersion)
		min_matrix = get_min_entropy(matrices)
		output_path = "/".join([args.output_folder, file_i + ".txt"])
		write_output_matrix(output_path, min_matrix)



if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--root-folder', type=str, nargs='?', help='folder containing all the runs')
	parser.add_argument('--matrices-folder', type=str, nargs='?', help='name of the matrix folder in each model folder')
	parser.add_argument('--model-prefix', type=str, default="run", nargs='?', help='prefix name for the models folders')
	parser.add_argument('--number', type=int, default=5, nargs='?', help='number of models to average')
	parser.add_argument('--output-folder', type=str, nargs='?', help='folder for storing individual files')
	parser.add_argument('--dispersion', type=float, nargs='?', help='ANE with penalization')
	parser.add_argument('--ids-file', type=str, nargs='?', help='id files')
	parser.add_argument('--transformer', default=False, action='store_true', help='set for transformer path getter')
	parser.add_argument('--pervasive', default=False, action='store_true', help='set for pervasive path getter')
	args = parser.parse_args()
	if not args.root_folder or not args.matrices_folder or not args.output_folder:
		parser.print_help()
		sys.exit(1)
	wrapper(args)
