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

def get_votes(members, N):
    votes = list()
    buckets = dict()
    for token, entropy, frequency in members:
        if frequency not in buckets:
            buckets[frequency] = list()
        buckets[frequency].append([token, entropy])
    for key in buckets.keys():
        buckets[key].sort(key=lambda x: x[1], reverse=False)
    sorted_keys = list(buckets.keys())
    sorted_keys.sort(reverse=True)
    for key in sorted_keys:
        for i in range(len(buckets[key])):
            if N == 0:
                break
            votes.append(buckets[key][i][0])
            N -= 1
    return votes

def cluster_voting(members, N, threshold, key):
    if threshold < 1:
        print(len(members))
        members = filter_members(members, threshold)
        print(len(members))
    members.sort(key=lambda x: x[2],reverse=True) #sorts per frequency
    if N == -1:
        return [element[0] for element in members]
    return get_votes(members, N)

def generate_lexicon(clusters, N, threshold):
    lexicon = list()
    for translation in clusters:
        vote = cluster_voting(clusters[translation], N, threshold, translation)
        lexicon += vote
    return lexicon

def generate():
    clusters = read_cluster(sys.argv[1])
    N = int(sys.argv[2])
    threshold = float(sys.argv[3])
    lexicon = generate_lexicon(clusters, N, threshold)
    lexicon = list(set(lexicon))
    utils.write_file(sys.argv[4], lexicon)


'''

things to change

1) filter clusters per entropy
2) 

'''

if __name__ == "__main__":
    generate()