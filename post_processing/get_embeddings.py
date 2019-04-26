import codecs, sys
import utils


def find_embeddings(f_path, keys):
    embeddings = list()
    with codecs.open(f_path,"r","utf-8") as input_file:
        for line in input_file:
            key = line.split(" ")[0]
            if key in keys:
                embeddings.append(line.strip())
                keys.remove(key)
            if keys == []:
                break 
    return embeddings, keys


def process():
    embeddings = sys.argv[1]
    words = utils.read_file(sys.argv[2])
    embeddings, not_found = find_embeddings(embeddings, words)

    utils.write_file("my_embeddings.txt", embeddings)
    utils.write_file("oov.txt", not_found)


if __name__ == "__main__":
    process()