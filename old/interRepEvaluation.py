import sys
import codecs

def read_file(path):
	return [line.strip("\n").split(" ") for line in codecs.open(path,"r","UTF-8")]

def get_dictionary(sentences, removeUnigrams):
    dict_list =[]
    for sentence in sentences:
        dict_list += sentence
    dict_list = list(set(dict_list))
    if removeUnigrams:
        for element in dict_list:
            if len(element) == 1 or ("\'" in element and len(element) == 2):
                dict_list.remove(element)
    return set(dict_list)

def get_correct_words(goldStandard, intermediate):
    correct_words = []
    correct_afix = []
    print len(intermediate)
    for i in range(0, len(goldStandard)):
        for word in intermediate[i]: #for each word in a sentence only partially segmented
            if len(word) > 1 and not "\'" in word: #excludes words not segmented and the prepositions which we only will know if are correctly segmented in the end
                #print word
                for gold in goldStandard[i]:
                    if word in gold and word != gold and not "\'" in word: #if the intermediate word is an afix
                        correct_afix.append(word) #afix
                        #print word, gold
                    elif word == gold:
                        print word, gold
                        correct_words.append(word)
    return set(correct_words), set(correct_afix)


def get_subwords(goldStandard, intermediate):
    pass




def main():
    goldStandard = read_file(sys.argv[1])
    intermediate = read_file(sys.argv[2])

    words, afixes = get_correct_words(goldStandard, intermediate)
    print len(words), len(afixes)
    #print len(get_correct_words(goldStandard, intermediate))
    print len(get_dictionary(intermediate, True))


    #get correct words and subwords
    #work on sentence level


if __name__ == '__main__':
    main()
