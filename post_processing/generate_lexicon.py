import codecs, sys, utils


def read_cluster(f_path):
    flag = True
    clusters = dict()
    last_key = None
    with codecs.open(f_path,"r","utf-8") as input_file:
        for line in input_file:
            if line.strip() == "":
                flag = True
            elif flag: # new cluster
                flag = False
                key = line.split("\t")[0]
                clusters[key] = list()
                last_key = key
            else:
                elements = line.strip().split("\t")
                clusters[last_key].append([elements[0], float(elements[1]), int(elements[2])])
    return clusters


def filter_members(lst, threshold):
    return [element for element in lst if element[1] <= threshold]

def cluster_voting(members, N, threshold, key):
    votes = list()
    if threshold:
        members = filter_members(members, threshold)
    members.sort(key=lambda x: x[2]) #sorts per frequency
    for i in range(N):
        if i >= len(members):
            break
        votes.append("\t".join([members[i][0], key]))
    return votes

def generate_lexicon(clusters, N, threshold):
    lexicon = list()
    for translation in clusters:
        vote = cluster_voting(clusters[translation], N, threshold, translation)
        lexicon += vote
    return lexicon

def generate():
    clusters = read_cluster(sys.argv[1])
    N = int(sys.argv[2])
    threshold = None if len(sys.argv) < 4 else float(sys.argv[3])
    lexicon = generate_lexicon(clusters, N, threshold)
    utils.write_file(sys.argv[1] + ".lexicon", lexicon)

if __name__ == "__main__":
    generate()