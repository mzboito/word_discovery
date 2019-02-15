import sys, codecs


#2 entries per epoch

#starts after line
#| max tokens per GPU = 2000 and max sentences per GPU = None


#loss, nll_loss, ppl, wps, ups, wpb, bsz, num_updates, lr, gnorm, clip, oom, wall, train_wall, valid_loss, valid_nll_loss, valid_ppl, num_updates

col = ["epoch",'loss', 'ppl', 'wps', 'ups', 'wpb', 'bsz', 'num_updates', 'lr', 'gnorm', 'clip', 'oom', 'wall', 'train_wall', "valid on 'valid' subset", 'valid_loss', 'valid_ppl', 'num_updates', 'best']

def read_ugly_file(f_path):
    dictionary = dict()
    start = False
    with codecs.open(f_path, "r","utf-8") as input_file:
        for line in input_file:
            if start:
                try:
                    line = line.replace(" | ", "| ").strip().split("| ")
                    key = line[1].replace("epoch ","")
                    try:
                        dictionary[int(key)] += clean_line(line[2:])
                    except KeyError:
                        dictionary[int(key)] = clean_line(line[2:])
                except Exception:
                    print(line)
                    #exit(1)
            elif "max tokens per GPU =" in line:
                start = True
    return dictionary 

def clean_line(e_list):
    for i in range(len(e_list)):
        if "valid on " in e_list[i]:
            pass
        else:
            e_list[i] = e_list[i].split(" ")[1]
    return e_list

def write_table(d, output_file):
    with open(output_file,"w") as output_file:
        output_file.write("\t".join(col) + "\n")
        #print(d.keys())
        for key in d.keys():
            output_file.write("\t".join([str(key)] + d[key]) + "\n")



def parser():
    entry_file = sys.argv[1]
    output_file = entry_file + ".clean"
    d = read_ugly_file(entry_file)
    write_table(d, output_file)




if __name__ == "__main__":
    parser()
