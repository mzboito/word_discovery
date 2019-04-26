import sys, codecs, glob, argparse
import utils, soft2hard
from pprint import pprint


def bpe_mapping(matrix, sentence):
	bpe_sentence = matrix[0]
	index_mapping = list()
	flag = False
	for i in range(1,len(bpe_sentence)): #first position is empty
		if "@" in bpe_sentence[i] and not flag:
			index_mapping.append([i]) # first part of a sliced word
			flag = True
		elif flag:
			index_mapping[-1].append(i) 
			if "@" not in bpe_sentence[i]: # last part of a sliced word
				flag = False
		else: #flag flase
			index_mapping.append([i])
			
	#print(bpe_sentence)
	#print(index_mapping)
	#print(sentence)
	assert len(index_mapping) == len(sentence)
	return index_mapping


def get_average_value(matrix_line, word_index):
	return str(sum([float(matrix_line[i]) for i in word_index]) / (len(word_index)*1.0))


def get_max_value(matrix_line, word_index):
	index = word_index[0]
	best = float(matrix_line[index])
	for i in range(1,len(word_index)):
		current_index = word_index[i]
		current_value = float(matrix_line[current_index])
		if current_value > best:
			best = current_value
			index = current_index
	return str(best)

def process_bpe(matrix, index_mapping, reference, function):
	new_matrix = [[0 for col in range(len(reference)+1)] for row in range(len(matrix))]
	new_matrix[0] = [""] + reference
	for row in range(1,len(matrix)):
		new_matrix[row][0] = matrix[row][0]
		for col in range(len(index_mapping)):
			word_index = index_mapping[col]
			if len(word_index) == 1:
				new_matrix[row][col+1] = matrix[row][word_index[0]]
			else:
				new_value = function(matrix[row], word_index)
				new_matrix[row][col+1] = new_value
	return new_matrix


def process(args):
	sentencesPaths = glob.glob(args.matrices_prefix + "*.txt")
	french_ref = utils.read_file(args.reference)
	for index in range(1, len(sentencesPaths)+1):
		f_path = soft2hard.get_path(index, sentencesPaths)
		file_name = f_path.split("/")[-1] 
		matrix = utils.read_matrix_file(f_path)
		reference = french_ref[index-1].replace("  "," ").split(" ")
		reference = reference + ["</S>"] if reference[-1] != '' else reference[:-1] + ["</S>"]
		#print(f_path)
		#print(matrix[0])
		#print(reference)
		index_mapping = bpe_mapping(matrix, reference)
		#print(index_mapping)
		if args.avg:
			new_matrix = process_bpe(matrix, index_mapping, reference, get_average_value)
		elif args.max:
			new_matrix = process_bpe(matrix, index_mapping, reference, get_max_value)
		
		'''for row in matrix:
			print("\t".join(row))
		print()
		for row in new_matrix:
			print("\t".join(row))
		'''
		utils.write_output_matrix(args.output_folder + file_name, new_matrix)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--matrices-prefix', type=str, nargs='?', help='matrices prefix')
	parser.add_argument('--reference', type=str, nargs='?', help='word reference for the generated bpe')
	parser.add_argument('--output-folder', type=str, nargs='?', help='folder for storing individual files')
	parser.add_argument('--avg', default=False, action='store_true', help='averages the probabilities for BPEs from the same word')
	parser.add_argument('--max', default=False, action='store_true', help='selects max probability from BPEs from the same word')
	args = parser.parse_args()
	if len(sys.argv) < 3 or not args.matrices_prefix:
		parser.print_help()
		sys.exit(1)
	process(args)