import sys, codecs, glob, utils, argparse

def is_new(token, lst):
    for element, _ in lst:
        if token == element:
            return False
    return True

def read_vocab_multiple_files(path_raw, path_clean):
    labs_path = glob.glob(path_raw + "/*")
    types_list = []
    frequency_dict = dict()
    for f_path in labs_path:
        #read same sentence twice (encoded and clean)
        tokens = [line.strip().split(" ")[2] for line in open(f_path, "r")] 
        tokens_clean = [line.strip().split(" ")[2] for line in open(f_path.replace(path_raw, path_clean).replace(".encoded","") , "r")]
        for i in range(len(tokens)): #for every token in the sentence
            if tokens[i] != "SIL" and is_new(tokens[i], types_list):
                types_list.append([tokens[i],tokens_clean[i].lower()])
        for element in tokens_clean: #adds frequencies for list
            element = element.lower()
            if element in frequency_dict:
                frequency_dict[element] += 1
            elif element != "sil":
                frequency_dict[element] = 1
    return types_list, frequency_dict



def read_vocab_single_file(path_raw, path_clean):
    raw_sentences = utils.read_file(path_raw)
    clean_sentences = utils.read_file(path_clean)
    assert len(raw_sentences) == len(clean_sentences)
    types_list = []
    frequency_dict = dict()
    for i in range(len(raw_sentences)):
        #read same sentence twice (encoded and clean)
        tokens = raw_sentences[i].split(" ")
        tokens_clean = clean_sentences[i].split(" ")
        for i in range(len(tokens)): #for every token in the sentence
            if tokens[i] != "SIL" and is_new(tokens[i], types_list):
                types_list.append([tokens[i],tokens_clean[i].lower()])
        for element in tokens_clean: #adds frequencies for list
            element = element.lower()
            if element in frequency_dict:
                frequency_dict[element] += 1
            elif element != "sil":
                frequency_dict[element] = 1
    return types_list, frequency_dict


def write_vocabulary(f_path, types, dictionary):
    with codecs.open(f_path, "w","utf-8") as output_file:
        for word_lst in types:
            output_file.write("\t".join(word_lst + [str(dictionary[word_lst[1].lower()])]) + "\n")

def generate(args):
    
    path_raw = args.raw_wrd
    path_clean = args.clean_wrd

    if args.single_file:
        types, frequency = read_vocab_single_file(path_raw, path_clean)
    else:
        types, frequency = read_vocab_multiple_files(path_raw, path_clean)

    output_file = args.output_file
    write_vocabulary(output_file, types, frequency)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw-wrd', type=str, nargs='?', help='path for raw .wrd labs')  
    parser.add_argument('--clean-wrd', type=str, nargs='?', help='path for clean .wrd labs')
    parser.add_argument('--single-file', default=False, action='store_true', help='vocab file')
    parser.add_argument('--output-file', type=str, nargs='?', help='name for output file')
    args = parser.parse_args()
    generate(args)