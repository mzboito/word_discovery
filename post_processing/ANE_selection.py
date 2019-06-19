# -*- coding: utf-8 -*-

import sys, codecs, argparse

def get_merger_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument('-lang1','--lang1-entropy-file', type=str, nargs='?', help='name of the entropy file with matrix ANE information')
	parser.add_argument('--lang1-folder', type=str, nargs='?', help='name of the matrix folder in each model folder')
	parser.add_argument('-lang2','--lang2-entropy-file', type=str, nargs='?', help='name of the entropy file with matrix ANE information')
	parser.add_argument('--lang2-folder', type=str, nargs='?', help='name of the matrix folder in each model folder')
	parser.add_argument('--output-file', type=str, nargs='?', help='paths of the chosen files')
	return parser

def read_summary_file(f_path):
	return [line.strip().split("\t")[:2] for line in codecs.open(f_path,"r","utf-8")][1:]

def normalize(lang_list): 
	# x new = observation - x min / xmax - xmin
	values = [float(element[1]) for element in lang_list]
	
	for i in range(len(lang_list)):
		value = float(lang_list[i][1])
		new_value = (value - min(values)) / (max(values) - min(values))
		lang_list[i][1] = new_value
	
	return lang_list


def merger(args):
	# read files
	lang1 = read_summary_file(args.lang1_entropy_file)
	lang2 = read_summary_file(args.lang2_entropy_file)
	assert len(lang1) == len(lang2)
	#print(len(lang1), len(lang2))
	# normalize entropy
	lang1 = normalize(lang1)
	lang2 = normalize(lang2)
	

	# select best entropy
	ids_dict = dict()

	#print(len(lang1), len(lang2))
	for i in range(len(lang1)):
		assert lang1[i][0] == lang2[i][0], "id mismatch"
		if float(lang1[i][1]) <= float(lang2[i][1]):
			ids_dict[lang1[i][0]] = (args.lang1_folder, lang1[i][1])
		else:
			ids_dict[lang1[i][0]] = (args.lang2_folder, lang2[i][1])


	assert len(lang1) == len(ids_dict.keys())

	# write output file 
	with open(args.output_file,"w") as output_file:
		for key in ids_dict.keys():
			output_file.write("/".join([ids_dict[key][0], key]) + "\n")
	# write summary
	with open(args.output_file+".summary","w") as output_file:
		output_file.write("\t".join(["id","avg_entropy","#tokens","avg_token_length"]) + "\n")
		for key in ids_dict.keys():
			output_file.write("\t".join([key, str(ids_dict[key][1])]) + "\n")


if __name__ == '__main__':
	parser = get_merger_parser()
	args = parser.parse_args()
	if len(sys.argv) < 3:
		parser.print_help()
		sys.exit(1)
	merger(args)
