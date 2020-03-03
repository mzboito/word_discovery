'''
The input of this script should be two segmentations (one of them can be the gold segmentation, or even dpseg). The script computes the intersection between set1 and set2 with respect to the size of set2
'''
import sys, codecs
from avg_token_length import read_file

def load_vocab(f_path):
    sentences = read_file(f_path)
    vocab = list()
    for sentence in sentences:
        for word in sentence:
            if not word in vocab:
                vocab.append(word)
    return vocab

def process():
    set1 = load_vocab(sys.argv[1])
    set2 = load_vocab(sys.argv[2])

    intersection = len(set(set1) & set(set2)) * 1.0
    print(intersection)
    percentage = intersection / len(set2) * 100
    print(percentage)

if __name__ == "__main__":
    process()
