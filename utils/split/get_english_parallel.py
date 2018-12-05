import sys
import glob

keys = ["dev","test", "train"]
suffixes = [".phn.unseg", ".fr"]

def assert_corpus(corpus):
    for split in keys:
        sentences = [[], []]
        for i in range(len(suffixes)):
            sentences[i] = [corpus[split][s_id][suffixes[i]] for s_id in corpus[split].keys()]
        assert len(sentences[0]) == len(sentences[1])

def write_corpus(corpus, keys):
    split_name = "+".join(keys) if len(keys) >1 else keys[0]
    for suffix in suffixes:
        with open(split_name + suffix,"w") as output_file:
            with open(split_name + ".ids","w") as ids_file:
                for split in keys:
                    for s_id in corpus[split].keys():
                        output_file.write(corpus[split][s_id][suffix] + "\n")
                        ids_file.write(s_id + "\n")

def read_file(path):
    return [line.strip("\n") for line in open(path,"r")]

def main():
    root_folder = sys.argv[1]
    corpus = dict()
    paths = dict()

    for split in keys:
        #generate the core dict with the ids
        corpus[split] = dict()
        split_ids = read_file(root_folder + "/" + split + ".ids")
        for split_id in split_ids:
            corpus[split][split_id] = dict()
        #put the sentences inside each split
        for suffix in suffixes:
            paths = glob.glob(root_folder + "/" + split + "/*" + suffix)
            for f_path in paths:
                s_id = f_path.split("/")[-1].split(".")[0]
                try:
                    corpus[split][s_id][suffix] = read_file(f_path)[0]
                except KeyError:
                    print("INVALID ID {} for SPLIT {}".format(s_id, split))
                    sys.exit(1)
    assert_corpus(corpus)
    write_corpus(corpus, list(keys[0]))
    write_corpus(corpus, keys[1:])


if __name__ == "__main__":
    main()