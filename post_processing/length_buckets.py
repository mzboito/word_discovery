import sys, codecs, utils

def add_sentence(dictionary, s1, s2):
    length = len(s1.split(" "))
    for key in dictionary.keys():
        if length <= key:
            dictionary[key].append([s1,s2])
            break
    return dictionary

def generate_buckets(gold, segmentation):
    lengths = dict()
    for i in range(20,120,20):
        lengths[i] = []
    for i in range(len(gold)):
        lengths = add_sentence(lengths, gold[i], segmentation[i])
    return lengths

def write_buckets(f_path, buckets):
    for key in buckets.keys():
        with codecs.open(".".join([f_path, str(key), "hs"]), "w","utf-8") as output_seg:
            with codecs.open(".".join([f_path, str(key), "wrd"]), "w","utf-8") as output_gold:
                for element in buckets[key]:
                    gold = element[0]
                    seg = element[1]
                    output_seg.write(seg + "\n")
                    output_gold.write(gold + "\n")
                        

def generate():
    segmentation = utils.read_file(sys.argv[1]) #.hs
    gold = utils.read_file(sys.argv[2]) #.wrd

    assert len(segmentation) == len(gold)
    output_prefix = sys.argv[3] 
    buckets = generate_buckets(gold, segmentation)
    write_buckets(output_prefix, buckets)



if __name__ == "__main__":
    generate()