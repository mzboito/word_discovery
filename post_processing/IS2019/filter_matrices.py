import sys



def run():
    dictionary = dict()
    with open(sys.argv[1],"r") as input_file:
        for line in input_file:
            s = line.split("\t")
            f = s[0]
            entropy = s[1][:3]
            if not entropy in dictionary:
                dictionary[entropy] = list()
            dictionary[entropy].append(f)
    

    del dictionary["avg"]

    for key in dictionary.keys():
        f_key = str(float(key) + 0.1)[:3]
        with open(sys.argv[2] + "_" + f_key, "w") as output_file:
            for element in dictionary[key]:
                
                output_file.write(element+"\n")



if __name__ == "__main__":
    run()