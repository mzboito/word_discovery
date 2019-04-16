import sys, glob, argparse

RANKS =  [50, 200, 500, 1000, 2000, 3000, 5000]

class TableElement():
    def __init__(self, clean_type, d_type, entropy, frequency, flag):
        self.clean_type = clean_type
        self.type = d_type
        self.entropy = entropy
        self.frequency = frequency
        self.flag = flag
    
    def toString(self):
        return "\t".join([self.clean_type, self.type, self.entropy, str(self.frequency), str(self.flag)])
    
    @staticmethod
    def print_head(table, n):
        for i in range(n):
            print(table[i].toString())

class TranslationElement(TableElement):
    def __init__(self, clean_type, d_type, d_translation, entropy, frequency, flag):
        super().__init__(clean_type, d_type, entropy, frequency, flag)
        self.translation = d_translation

    def toString(self):
        return "\t".join([self.clean_type, self.type, self.translation, self.entropy, str(self.frequency), str(self.flag)])

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

def generate_gold(path_raw, path_clean):
    labs_path = glob.glob(path_raw + "/*")
    types_list = []
    frequency_dict = dict()
    for f_path in labs_path:
        #read same sentence twice (encoded and clean)
        tokens = [line.strip().split(" ")[2] for line in open(f_path, "r")] 
        tokens_clean = [line.strip().split(" ")[2] for line in open(f_path.replace(path_raw, path_clean).replace(".encoded","") , "r")]
        for i in range(len(tokens)): #for every token in the sentence
            if tokens[i] != "SIL" and tokens[i] not in types_list:
                types_list.append((tokens[i],tokens_clean[i]))
        for element in tokens_clean: #adds frequencies for list
            element = element.lower()
            if element in frequency_dict:
                frequency_dict[element] += 1
            elif element != "sil":
                frequency_dict[element] = 1
    return types_list, frequency_dict

def in_types(token, types_list):
    for encoded, clean in types_list:
        if token == encoded:
            return clean
    return None

def generate_types_table(f_path, types_list, frequency_dict):
    table = list()
    with open(f_path,"r") as csv_file:
        for line in csv_file:
            elements = line.strip().split("\t")
            discovered_token = elements[0]
            entropy = elements[1]
            element, flag = check_token(discovered_token, types_list)
            gold_freq = frequency_dict[element] if flag == 1 else 0
            obj = TableElement(element, discovered_token, entropy, gold_freq, flag)
            table.append(obj)
    return table

def generate_translation_table(f_path, types_list, frequency_dict):
    table = list()
    with open(f_path,"r") as csv_file:
        for line in csv_file:
            elements = line.strip().split("\t")
            discovered_token = elements[0].split("_")[0]
            discovered_translation = elements[0].split("_")[1]
            entropy = elements[1]
            element, flag = check_token(discovered_token, types_list)
            gold_freq = frequency_dict[element] if flag == 1 else 0
            obj = TranslationElement(element, discovered_token, discovered_translation, entropy, gold_freq, flag)
            table.append(obj)
    return table

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

def write_table(f_path, table, threshold=None):
    counter = 0
    file_name = f_path.replace(".csv",".cleaned.csv") if not threshold else f_path.replace(".csv","."+str(threshold)+".cleaned.csv")
    with open(file_name,"w") as output_file:
        if threshold:
            for element in table:
                if counter < threshold:
                    if element.flag == 1:
                        counter += element.flag #count number of true types
                    output_file.write(element.toString() + "\n")
        else:
            for element in table:
                output_file.write(element.toString() + "\n")

def generate(args):
    wrd_clean = args.clean_wrd
    wrd = args.wrd
    types_list, frequency_dict = generate_gold(wrd, wrd_clean)
    if args.type_entropy:
        f_path = args.type_entropy
        table = generate_types_table(f_path, types_list, frequency_dict)
    elif args.translation_entropy:
        f_path = args.translation_entropy
        table = generate_translation_table(f_path, types_list, frequency_dict)
    elif args.ngram_entropy:
        f_path = args.ngram_entropy
        table = generate_ngram_table(f_path, types_list, frequency_dict)
    else:
        raise Exception("MISSING ENTROPY TABLE")
    
    table.sort(key=lambda x: x.entropy)
    write_table(f_path, table)
    for threshold in RANKS:
        write_table(f_path, table, threshold=threshold)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--clean-wrd', type=str, nargs='?', help='path for clean .wrd labs')
    parser.add_argument('--wrd', type=str, nargs='?', help='path for raw (encoded) .wrd labs')
    parser.add_argument('--type-entropy', type=str, nargs='?', help='path for generated ranking')
    parser.add_argument('--translation-entropy', type=str, nargs='?', help='path for generated ranking')
    parser.add_argument('--ngram-entropy', type=str, nargs='?', help='path for generated ranking')
    args = parser.parse_args()
    generate(args)
