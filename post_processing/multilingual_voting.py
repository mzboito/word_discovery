import sys, utils, codecs
import math


def clean(line):
    if line[0] == " ":
        line = line[1:]
    if line[-1] == " ":
        line = line[:-1]
    return line

def read_segmentation(f_path): 
    #the output is a list of indexes. Example: [1,5,7] means there is a boundary after the first, fifth and seventh character in the sentence
    sentences_i = list()
    with codecs.open(f_path, "r","utf-8") as output_file:
        for line in output_file:
            line = clean(line)
            s_indexes = list()
            count_char = 0
            for char in line:
                if char == " ":
                    s_indexes.append(count_char)
                else:
                    count_char += 1
            sentences_i.append(s_indexes)
    return sentences_i

def generate_dictionary(candidates, s_index):
    votes = dict()
    for lang in candidates:
        for index in lang[s_index]:
            if not index in votes.keys():
                votes[index] = 1
            else:
                votes[index] += 1
    return votes

def merge_index_lists(candidates, s_index, threshold):
    number_votes = len(candidates)
    if threshold == 1:
        i = s_index
        final_index = candidates[0][i] #candidates is a list of a list of indexes
        for j in range(1,number_votes):
            final_index = list(set(final_index) & set(candidates[j][i]))
    elif threshold == 0:
        i = s_index
        final_index = candidates[0][i]
        for j in range(1,number_votes):
            final_index = sorted(list(set(final_index + candidates[j][i])))
    else: #threshold \in (0,1)
        agreement = math.ceil(number_votes * threshold) #  /!\ Decided for ceil
        votes = generate_dictionary(candidates, s_index) #computes votes
        final_index = [key for key in votes.keys() if votes[key] >= agreement] #filter using the agreement
    return final_index

def voting(candidates, threshold):
    number_sentences = len(candidates[0])
    final_indexes = list()
    for i in range(number_sentences):
        final_index = merge_index_lists(candidates, i, threshold)
        final_indexes.append(final_index)
    return final_indexes

def generate_segmentation(reference, boundaries):
    corpus = list()
    for i in range(len(reference)): #for every sentence
        sentence = reference[i]
        indexes = boundaries[i]
        new_segmentation = ""
        for j in range(len(sentence)):
            if j in indexes:
                new_segmentation += " "
            char = sentence[j]
            new_segmentation += char
        corpus.append(new_segmentation)
    return corpus            

def write_output(f_path, corpus):
    with codecs.open(f_path, "w", "utf-8") as output_file:
        for sentence in corpus:
            output_file.write(sentence + "\n")

def main():
    print(sys.argv)
    corpus_unseg = [line.strip().replace(" ","") for line in codecs.open(sys.argv[1], "r","utf-8")]
    output_file = sys.argv[2]
    threshold = float(sys.argv[3])
    N = int(sys.argv[4])
    if N < 2 or len(sys.argv) < (N + 4):
        print("Invalid number N of languages or incorrect number of paths")
        exit(1)
    candidates = list()
    for i in range(N):
        candidates.append(read_segmentation(sys.argv[i+5]))
    for i in range(N):
        assert len(corpus_unseg) == len(candidates[i]), "Files mismatch"
    final_boundaries = voting(candidates, threshold)
    final_segmentation = generate_segmentation(corpus_unseg, final_boundaries)
    write_output(output_file ,final_segmentation)

if __name__ == "__main__": 
    #python multilingual_voting.py <unseg version> <threshold> <N> <list of paths for languages segmentation>
    main()