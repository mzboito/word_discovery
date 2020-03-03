'''
This script receives a segmentation and the gold standard. It computes the frequency of all the types, and then sets all the discovered (correct) types into frequency buckets,
in order to verify the network behavior with respect to the frequency
'''
import sys, math
from avg_token_length import read_file
from lexicon_intersection import load_vocab

buckets=10

def load_dict(f_path):
    sentences = read_file(f_path)
    vocab = dict()
    for sentence in sentences:
        for word in sentence:
            if word in vocab:
                vocab[word]+=1
            else:
                vocab[word]=1
    return vocab

def find_key(v_max, w_dict):
    for key in w_dict:
        if w_dict[key] == v_max:
            return key
    raise Exception

def generate_buckets(gold_dict):
    b_dict = dict()
    values = len(gold_dict)
    bucket = math.floor(values/buckets)
    id_bucket = 100
  
    while values >=0:
        this_bucket = bucket
        while this_bucket > 0:
            gold_values = gold_dict.values()
            if not gold_values:
                break  #finished 
            new_max = max(gold_dict.values())
            key = find_key(new_max, gold_dict)
            if not id_bucket in b_dict:
                b_dict[id_bucket] = list()
            b_dict[id_bucket].append(key)
            del gold_dict[key]
            this_bucket -= 1

        id_bucket -= buckets
        values -= bucket

    #in case of an odd division, put the remain in the lowest frequency possible
    if 0 in b_dict.keys():
        b_dict[buckets] = b_dict[buckets] + b_dict[0]
        del b_dict[0]
    
    return b_dict

def segmentation_buckets(vocab, b_dict):
    #create new bucket
    e_dict = dict()
    for b in b_dict:
        e_dict[b] = list()
        for word in b_dict[b]:
            if word in vocab:
                e_dict[b].append(word)
    return e_dict

def evaluation(vocab, b_dict):
    e_dict = segmentation_buckets(vocab, b_dict)
    for k in e_dict:
        correct = len(e_dict[k])*1.0
        gold = len(b_dict[k])*1.0
        print("BUCKET",k, "SIZE",gold)
        print("Recall",end=" ")
        print(correct/gold)

    
def process():
    segmentation = load_vocab(sys.argv[1])
    gold_dico = load_dict(sys.argv[2])
    buckets_dict = generate_buckets(gold_dico)
    evaluation(segmentation, buckets_dict)

    



if __name__ == "__main__":
    process()