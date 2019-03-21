import sys, codecs

def clean_dpseg(dpseg_out):
    dpseg_clean =[]
    flag = False
    for i in range(len(dpseg_out)):
        if u'_nstrings=xxx' == dpseg_out[i]:
            break
        if flag:
            dpseg_clean.append(dpseg_out[i])
        if "State:" in dpseg_out[i]:
            flag = True
    return dpseg_clean

def match(lst1, string, sup_2, sup_3):
    match = False
    while not match:
        if len(lst1[0].replace(" ","")) == len(string.replace(" ","")): #equals don't work because the output is shit
            return lst1, sup_2, sup_3
        else:
            del lst1[0]
            del sup_2[0]
            del sup_3[0]
    return None, None, None

def write_file(f_path, lst):
    with codecs.open(f_path, "w", "utf-8") as output_file:
        for element in lst:
            output_file.write(element + "\n")

def remove_sil(lst):
    return [element for element in lst if element != "SIL"]

def get_original(f_path):
    return [line.strip() for line in codecs.open(f_path, 'r', 'utf-8')][0]

def solver():
    ids = [line.strip() for line in open(sys.argv[1],"r")]
    unseg = [line.strip() for line in codecs.open(sys.argv[2],"r","utf-8")]
    dpseg_out = [line.strip() for line in codecs.open(sys.argv[3], "r", "UTF-8", errors="replace")] 
    unseg_phn = [line.strip() for line in codecs.open(sys.argv[4],"r","utf-8")]
    assert len(ids) == len(unseg), "ids don't match the reference file"

    dpseg_seg = clean_dpseg(dpseg_out)

    filtered = []
    segmentation = []
    new_ids = []
    for sentence in dpseg_seg:
        unseg, ids, unseg_phn  = match(unseg, sentence, ids, unseg_phn)
        if unseg:
            filtered.append(sentence)
            segmentation.append(unseg_phn[0])
            new_ids.append(ids[0])
            del ids[0]
            del unseg_phn[0]
            del unseg[0]

        else:
            raise Exception("life sucks")

    

    dpseg_clean = filtered

    print(len(segmentation), len(dpseg_clean))
    assert len(segmentation) == len(dpseg_clean)

    for j in range(len(segmentation)):
        line = remove_sil(segmentation[j].split(" "))
        dpseg_line = dpseg_clean[j]
        id_s = remove_sil(get_original(sys.argv[5] + "/" + new_ids[j].split("_")[0] + "/true_phones/" + new_ids[j] + ".phn.unseg").split(" "))
        #print(line, dpseg_line, id_s)
        index = 0
        new_line = ""
        for i in range(len(line)):
            if dpseg_line[index] == " ": #if found a boundary
                new_line += " "
                index+=1
            new_line += line[i] #adds the characters
            index+=1
        #print(new_line)
        #print(id_s)
        #print()
        segmentation[j] = new_line
        #print(new_line.replace(" ",""))
        #print("".join(id_s))
        assert len("".join(id_s)) == len(new_line.replace(" ","")) 
        #exit(1)



    write_file(sys.argv[1] + ".filtered", new_ids)
    #write_file(sys.argv[2] + ".filtered", unseg)
    #write_file(sys.argv[3] + ".filtered", filtered)
    #write_file(sys.argv[4] + ".filtered", unseg_phn)
    write_file(sys.argv[3] + ".filtered.output", segmentation)
    


if __name__ == "__main__":
    solver()
