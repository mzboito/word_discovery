# -*- coding: utf-8 -*-

import sys
import codecs
import glob

###################### SETTINGS ######################
att_matrices_folder = "att_matrices/"
files_folder = "files/"
folders_prefix = "run"
matrices_train_prefix = "train+dev" # "train"
matrices_dev_prefix = "dev"
dev_exists = False
train_max = 5130 #4616 
id_suffix = ".ids"
different_split = False
######################################################

def read_ids_file(f_path, intern_dict):
	count = 1
	with open(f_path, "r") as input_file: #reads train
		intern_dict = dict() #creates intern dict
		for line in input_file:
			intern_dict[line.strip()] = matrices_train_prefix +"."+ str(count) #{id name, file name on that folder}
			count +=1

def get_file_name(folder):
	return matrices_train_prefix + "." + folder[:-1] + id_suffix if different_split else matrices_train_prefix + id_suffix 

def load_files(root_folder, folders):
	files_dict = dict()
	for folder in folders:
		files_dict[folder] = [] #creates entry for folder
		file_name = get_file_name(folder)
		intern_dict = dict() #creates intern dict
		prefix_dir = root_folder + files_folder
		read_ids_file(prefix_dir + file_name, intern_dict)
		if dev_exists:
			file_name = file_name.replace(matrices_train_prefix,matrices_dev_prefix)
			read_ids_file(prefix_dir + file_name, intern_dict)
		files_dict[folder] = intern_dict
	return files_dict

def read_matrix(path):
	return [line.strip("\n").split("\t") for line in codecs.open(path,"r","UTF-8")]

def merge_matrices(matrices_list):
	num_lines = len(matrices_list[0])
	num_columns = len(matrices_list[0][0]) #+ 1
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
    output_path = path.replace(".lab", ".avgatt") + ".txt"
    with codecs.open(output_path, "w", "UTF-8") as outputFile:
        for line in matrix:
            try:
                outputFile.write("\t".join(line) + "\n")
            except TypeError:
                pass

def get_file_from_index(files_dict, folder, f_id):
	for key in files_dict[folder].keys():
		if files_dict[folder][key] == f_id:
			return key
	print("PROBLEM GETTING KEY FROM DICTIONARY:\nid: " + str(f_id) + " folder: " + folder + "\n")
	sys.exit(1)

def get_index_from_file(files_dict, folder, f_name):
	for key in files_dict[folder].keys():
		if key == f_name:
			return files_dict[folder][key]
	print("PROBLEM GETTING ID FROM DICTIONARY:\nfile: " + f_name + " folder: " + folder + "\n")
	sys.exit(1)

def find_matrices(root_folder, folders, files_dict, file_name):
	matrices = []
	for folder in folders:
		f_id = get_index_from_file(files_dict, folder, file_name)
		matrix_file = glob.glob(root_folder + folder + att_matrices_folder + f_id +".txt")
		matrix = read_matrix(matrix_file[0])
		matrices.append(matrix)
	if len(matrices) != len(folders):
		print("COULD NOT READ ALL THE MATRICES FOR FILE: " + file_name + "\n")
		sys.exit(1)
	else:
		size = len(matrices[0])
		for i in range(1, len(folders)):
			if len(matrices[i]) != size:
				print("PROBLEM WITH MATRIX SIZE: " + file_name + " folder: " + str(i+1) + "\n")
				sys.exit(1)

	return matrices

def print_settings(root_folder, output_folder, f_number):
	print()
	print("MERGING MATRICES SCRIPT: PRINTING SETTINGS")
	print()
	folders = []
	for i in range(1,f_number+1):
		folders.append(folders_prefix + str(i))
	print("\tON ROOT FOLDER {} LOOKING FOR {} FOLDERS".format(root_folder,",".join(folders)))
	print("\tTHE ATTENTION MATRICES SHOULD BE AT {}".format(att_matrices_folder))
	print("\tFILES FOLDER AT {} WITH ID SUFFIX {}".format(files_folder, id_suffix))
	print("\tTRAIN SIZE {} DIFFERENT SPLIT {}".format(train_max, different_split))
	print("\n")

def main():
	root_folder = sys.argv[1]
	output_folder = sys.argv[2]
	f_number = int(sys.argv[3])

	print_settings(root_folder, output_folder, f_number)

	folders = [folders_prefix+ str(i) + "/" for i in range(1,f_number+1)] #list folders

	files_dict = load_files(root_folder, folders) #load files

	size = len(files_dict[folders[0]])

	for i in range(1, f_number):
		if len(files_dict[folders[i]]) != size:
			print("PROBLEM READING THE LISTS (INDEX = " + str(i) + ")\n")
			sys.exit(1)
	for i in range(1, size+1):
		if i > train_max and dev_exists:
			file_i = get_file_from_index(files_dict, folders[0], matrices_dev_prefix + "." + str(i - train_max))
		else:
			file_i = get_file_from_index(files_dict, folders[0],  matrices_train_prefix + "." + str(i))
		matrices = find_matrices(root_folder, folders, files_dict, file_i)
		avg_matrix = merge_matrices(matrices)
		write_output(output_folder + file_i, avg_matrix)


if __name__ == '__main__':
	if len(sys.argv) < 4:
		print("USAGE: python merge_matrices.py <root folder> <output_folder> <number of runs>")
		print("/!\\ REMEMBER TO RE-SET INFORMATION AT THE HEADER OF THIS SCRIPT")
		sys.exit(1)
	main()
