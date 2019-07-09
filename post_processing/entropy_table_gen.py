import sys, glob, argparse, codecs, numpy, utils
import soft2hard as s2h

RANKS =  [50, 200, 500, 1000, 2000, 3000, 4000, 5000]

class TableElement():
    def __init__(self, clean_type, d_type, entropy, frequency, flag):
        self.clean_type = clean_type
        self.type = d_type
        self.entropy = entropy
        self.frequency = frequency
        self.flag = flag
    
    def toString(self):
        return "\t".join([self.clean_type, self.type, str(self.entropy), str(self.frequency), str(self.flag)])
    
    @staticmethod
    def print_head(table, n):
        for i in range(n):
            print(table[i].toString())

class TranslationElement(TableElement):
    def __init__(self, clean_type, d_type, d_translation, entropy, frequency, flag):
        super().__init__(clean_type, d_type, entropy, frequency, flag)
        self.translation = d_translation

    def toString(self):
        return "\t".join([self.clean_type, self.type, self.translation, str(self.entropy), str(self.frequency), str(self.flag)])

class NgramElement(TableElement):
    def __init__(self):
        self.objs = list()
        self.entropy = None
        self.flag = None

    def add(self, element):
        self.objs.append(element)
    
    def generate_flags(self):
        flag = "_".join([str(element.flag) for element in self.objs])
        gold = len(self.objs)*"1_"
        gold = gold[-1]
        self.flag = 1 if flag == gold else 0
        self.entropy = self.objs[0].entropy
        for obj in self.objs:
            assert obj.entropy == self.entropy
    
    def toString(self):
        clean = "_".join([element.clean_type for element in self.objs])
        encoded = "_".join([element.type for element in self.objs])
        entropy = self.objs[0].entropy
        gold_freq = "_".join([str(element.frequency) for element in self.objs])
        flag = "_".join([str(element.flag) for element in self.objs])
        return "\t".join([clean, encoded, entropy, gold_freq, flag, str(self.flag)])

def read_vocab(path_vocab):
    types = list()
    frequency = dict()
    with codecs.open(path_vocab,"r","utf-8") as vocab_file:
        for line in vocab_file:
            elements = line.strip().split("\t")
            phn_type = elements[0]
            wrd_type = elements[1]
            freq = int(elements[2])
            types.append((phn_type, wrd_type))
            frequency[phn_type] = freq
    return types, frequency

def in_types(token, types_list):
    for encoded, clean in types_list:
        if token == encoded:
            return clean
    return None

def generate_types_table(dictionary, types_list, frequency_dict):
    table = list()
    for key in dictionary.keys():
        discovered_token = key
        entropy = dictionary[key][0]
        element, flag = check_token(discovered_token, types_list)
        gold_freq = frequency_dict[discovered_token] if flag == 1 else 0
        obj = TableElement(element, discovered_token, entropy, gold_freq, flag)
        table.append(obj)
    #print(len(table))
    return table

def generate_translation_table(dictionary, types_list, frequency_dict):
    table = list()
    for key in dictionary.keys(): 
        discovered_token = key.split("##")[0]
        discovered_translation = key.split("##")[1]
        entropy = dictionary[key][0]
        element, flag = check_token(discovered_token, types_list)
        gold_freq = frequency_dict[discovered_token] if flag == 1 else 0#frequency_dict[element] if flag == 1 else 0
        obj = TranslationElement(element, discovered_token, discovered_translation, entropy, gold_freq, flag)
        table.append(obj)
    #print(len(types))
    #print(len(table))
    return table

def check_token(token, types_list):
    flag = 1
    element = in_types(token, types_list)
    if element:
        return element.lower(), flag
    flag +=1
    element = concatenation_check(token, types_list)
    if element:
        return element.lower(), flag
    flag +=1
    element = substring_check(token, types_list)
    if element:
        return element, flag
    return "Z-not-a-word", 0

def concatenation_check(token, types_list):
    '''we limited to search size 2 because otherwise we could end up on a 
    point in which everything is a concatenation (under-segmentation)'''
    for encoded, clean in types_list: #for every type
        if encoded == token[:len(encoded)]: #if found a possible prefix
            sub_token = token[len(encoded):] #removes it from the word
            sub_clean = in_types(sub_token, types_list)
            if sub_clean: 
                return "+".join([clean, sub_clean])
    return None

def substring_check(token, types_list):
    for encoded, clean in types_list:
        if token in encoded:
            return "-".join([clean.lower(), encoded.replace(token, "")])
    return None

def write_table(f_path, table, threshold=None, entropy_wall=None):
    counter = 0
    if threshold or entropy_wall:
        info = threshold if threshold else entropy_wall
        file_name = f_path.replace(".csv","."+str(info)+".csv")
    else:
        file_name = f_path
    with open(file_name,"w") as output_file:
        if threshold:
            for element in table:
                if counter < threshold:
                    if element.flag == 1:
                        counter += element.flag #count number of true types
                    output_file.write(element.toString() + "\n")
                else:
                    break
        elif entropy_wall:
            for element in table:
                if float(element.entropy) <= entropy_wall:
                    output_file.write(element.toString() + "\n")
                else:
                    break
        else:
            for element in table:
                output_file.write(element.toString() + "\n")

def filter_translation_table(table):
    ## since we align types to translations, we can end up having the same type twice
    table.sort(key=lambda x: x.entropy) #keep only the lowest entropy entry
    new_table = list()
    keys = list()
    for i in range(len(table)):
        element = table[i]
        if not element.type in keys:
            keys.append(element.type)
            new_table.append(element)
    return new_table

def generate_types_dictionary(dictionary):
    types_dict = dict()
    for key in dictionary.keys():
        for token, translation, entropy in dictionary[key]:
            if token not in types_dict:
                types_dict[token] = [[],[]]
            types_dict[token][0].append(entropy) #saves token ane
            types_dict[token][1].append(key) #saves ids

    for element in types_dict.keys():
        avg_entropy = sum(value for value in types_dict[element][0]) / len(types_dict[element][0])
        types_dict[element] = [avg_entropy, types_dict[element][1]]
    #print(len(types_dict.keys()))
    return types_dict

def generate_translation_dictionary(dictionary):
    #print("generating translation dictionary")
    translation_dict = dict()
    types = list()
    for key in dictionary.keys():
        for token, translation, entropy in dictionary[key]:
            if token not in types:
                types.append(token)
            entry = "##".join([token, translation])
            if entry not in translation_dict:
                translation_dict[entry] = [[],[]]
            translation_dict[entry][0].append(entropy)
            translation_dict[entry][1].append(key)
    teste = list()
    for element in translation_dict.keys():
        teste.append(element.split("##")[0])
        avg_entropy = sum(value for value in translation_dict[element][0]) / len(translation_dict[element][0])
        translation_dict[element] = [avg_entropy, translation_dict[element][1]]
    #print(len(types))
    #print(len(translation_dict.keys()))
    #print(len(set(teste)))
    return translation_dict

def generate_dictionary(args):
    #retrieve the matrices
    sentencesPaths = glob.glob(args.matrices_prefix+"*.txt") 
    #loads silence information
    silence_dict = utils.read_lab_files(args.silence) if args.silence else None
    CORPUS = dict()
    if args.individual_files:
        files_output_list = utils.read_file(args.individual_files)
        assert len(files_output_list) == len(sentencesPaths)

    for index in range(1, len(sentencesPaths)+1):
        file_path = sentencesPaths[index-1]
        file_name = ".".join(files_output_list[index-1].split("/")[-1].split(".")[:-1]) if args.individual_files else ".".join(file_path.split("/")[-1].split(".")[:-1])
        sil_list = silence_dict[file_name] if args.silence else None

        CORPUS = s2h.get_matrix_entropy(file_path, CORPUS, str_id=file_name, lab_lst = sil_list)
    if args.type_entropy:
        CORPUS = generate_types_dictionary(CORPUS)
    elif args.translation_entropy:
        CORPUS = generate_translation_dictionary(CORPUS)
    #utils.write_dictionary(output_path, CORPUS)
    return CORPUS

def generate_table(args, dictionary):
    types_list, frequency_dict = read_vocab(args.vocab)
    if args.type_entropy:
        #f_path = args.type_entropy
        table = generate_types_table(dictionary, types_list, frequency_dict)
        table.sort(key=lambda x: x.entropy)
    elif args.translation_entropy:
        #f_path = args.translation_entropy
        table = generate_translation_table(dictionary, types_list, frequency_dict)
        table = filter_translation_table(table)
    return table

def generate_ranking_files(args, table):
    f_path = args.output + ".csv"
    write_table(f_path, table)
    if not args.entropy_wall:
        for threshold in RANKS:
            write_table(f_path, table, threshold=threshold)
    else:
        for i in numpy.arange(0.1,1.1,0.1):
            i = numpy.around(i, decimals =1)
            write_table(f_path, table, entropy_wall=float(i))

def generate(args):
    print("1. EXTRACTING TYPES FROM SOFT-ALIGNMENT MATRICES")
    dictionary = generate_dictionary(args)

    print("2. GENERATING TABLE")
    table = generate_table(args, dictionary)
    
    print("3. CREATING THE RANKING FILES")
    generate_ranking_files(args, table)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    #parser.add_argument('--clean-wrd', type=str, nargs='?', help='path for clean .wrd labs')
    parser.add_argument('--matrices-prefix', type=str, nargs='?', help='prefix for the soft-alignment matrices')
    parser.add_argument('--individual-files', type=str, nargs='?', help='list of names for generating individual files')
    parser.add_argument('--silence', type=str, nargs='?', help='silence reference files')
    parser.add_argument('--vocab', type=str, nargs='?', help='vocab file')
    parser.add_argument('--output', type=str, nargs='?', help='name for the output file')
    #types of entropy 
    parser.add_argument('--type-entropy',  default=False, action='store_true', help='path for generated ranking')
    parser.add_argument('--translation-entropy', default=False, action='store_true', help='path for generated ranking')
    #parser.add_argument('--ngram-entropy',  default=False, action='store_true', help='path for generated ranking')
    #table type
    parser.add_argument('--entropy-wall', default=False, action='store_true', help='uses entropy threshold for generating ranking, on its absence, uses correct types')
    args = parser.parse_args()
    if not (args.translation_entropy or args.type_entropy):
        parser.print_help()
        sys.exit(1)
    generate(args)




'''def translation_entropy(f_path, dictionary):
    matrix = utils.read_matrix_file(f_path)
    discovered_tokens, index_list, discovered_translation = get_distributions(matrix)
    for i in range(len(discovered_tokens)):
        token = discovered_tokens[i].replace("</S>","")
        translation = discovered_translation[i]
        key = "_".join([token, translation])
        if len(token) > 0:
            if key not in dictionary:
                dictionary[key] = list()
            avg_entropy = get_average_entropy(matrix, index_list[i])
            dictionary[key].append((avg_entropy, f_path.split("/")[-1]))
    return dictionary
'''
'''def types_entropy(f_path, dictionary):
    matrix = utils.read_matrix_file(f_path)
    discovered_tokens, index_list, _ = get_distributions(matrix)
    for i in range(len(discovered_tokens)):
        token = discovered_tokens[i].replace("</S>","")
        if len(token) > 0:
            if token not in dictionary:
                dictionary[token] = list()
            avg_entropy = get_average_entropy(matrix, index_list[i])
            dictionary[token].append((avg_entropy, f_path.split("/")[-1]))
    return dictionary'''

'''#TO DO FIX ME
        elif args.type_entropy:
            output_path = args.output_file
            CORPUS = dict()
            for index in range(1, len(sentencesPaths)+1):
                file_path = sentencesPaths[index-1]
                CORPUS = get_matrix_entropy(file_path, CORPUS)
            utils.write_dictionary(output_path, TYPES)
        #TO DO FIX ME
        elif args.translation_entropy:
            output_path = args.output_file
            ALIGNED = dict()
            for index in range(1, len(sentencesPaths)+1):
                file_path = sentencesPaths[index-1]
                ALIGNED = translation_entropy(file_path, ALIGNED)
            utils.write_dictionary(output_path, ALIGNED)
    #TO DO FIX ME
    elif args.ngram_entropy:
        output_path = args.output_file
        NGRAMS = dict()
        for index in range(1, len(sentencesPaths)+1):
            file_path = sentencesPaths[index-1]
            NGRAMS = ngrams_entropy(file_path, NGRAMS, args.ngram_entropy)
        utils.write_dictionary(output_path, NGRAMS)''' 
'''
def generate_ngrams(dictionary, N):
    tokens = list(dictionary.keys()) #/!\ will not work correctly with python version < 3.6 (sorted dictionary)
    return list(zip(*[tokens[i:] for i in range(N)]))

def ngrams_entropy(f_path, dictionary, N=2):
    temp_dict = s2h.get_matrix_entropy(f_path, dict())
    temp_dict = generate_types_dictionary(temp_dict)
    sets = generate_ngrams(temp_dict, N)
    for ngram in sets:
        avg_entropy = 0.0
        for element in ngram:
            avg_entropy += temp_dict[element][0][0]
        avg_entropy /= N
        key = "_".join(list(ngram))
        if key not in dictionary:
            dictionary[key] = [(avg_entropy,f_path.split("/")[-1])]
        else:
            dictionary[key].append((avg_entropy,f_path.split("/")[-1]))
    return dictionary
    elif args.ngram_entropy:
        f_path = args.ngram_entropy
        table = generate_ngram_table(f_path, types_list, frequency_dict)
        table.sort(key=lambda x: x.entropy)

def generate_ngram_table(f_path, types_list, frequency_dict):
    table = list()
    with open(f_path,"r") as csv_file:
        for line in csv_file:
            ngram = NgramElement()
            elements = line.strip().split("\t")
            tokens = elements[0].split("_")
            entropy = elements[1]
            for token in tokens:
                element, flag = check_token(token, types_list)
                gold_freq = frequency_dict[element] if flag == 1 else 0
                obj = TableElement(element, token, entropy, gold_freq, flag)
                ngram.add(obj)
            ngram.generate_flags()
            table.append(ngram)
    return table
'''
