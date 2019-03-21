import sys
import codecs
import glob
SIL_token = "SIL"

def read_lab(f_path):
    labs = []
    with codecs.open(f_path,"r","utf-8") as input_file:
        for line in input_file:
            line = line.strip("\n").split(" ")
            labs.append(line[2])
    return labs

def read_segmentation(f_path):
    return [line.strip("\n") for line in codecs.open(f_path,"r","utf-8")][0]

def get_segmentation(f_path):
    f_path = glob.glob(f_path + ".*")[0]
    if not f_path:
        print("ID ERROR")
        sys.exit(1)
    return read_segmentation(f_path)

def merge_silence(segmentation, labs):
    new_segmentation = ""
    index_d = 0
    #initial_seg = segmentation
    segmentation = segmentation if segmentation[-1] != " " else segmentation[:-1]
    while(segmentation):
        len_pseudo = len(labs[index_d])
        if labs[index_d] == segmentation[0:len_pseudo]: #if pseudo == head
            new_segmentation+= labs[index_d]#add symbol
            segmentation = segmentation[len_pseudo:] #remove head
            index_d+=1 #go to next phone
        elif labs[index_d] == SIL_token: #if pseudo == SIL (therefore pseudo != head)
            if new_segmentation and new_segmentation[-1] == " ":
                new_segmentation += SIL_token + " " #add sil and go to next phone
            elif new_segmentation:
                new_segmentation+= " " + SIL_token + " " #add sil and go to next phone
            else:
                new_segmentation+= SIL_token + " " #add sil and go to next phone
            index_d+=1
        elif segmentation[0] == " ": #if head ins on a boundary
            new_segmentation += segmentation[0]
            segmentation = segmentation[1:] #add the segmentation mark and move next
        else: #something went terribly wrong
            print("ERROR MERGING LAB")
            print("segmentation = " + segmentation)
            print("pseudo_labs = " + labs[index_d])
            print("head = " + segmentation[0:len_pseudo])
            print("new segmentation = " + new_segmentation)
            sys.exit(1)
    while index_d < len(labs):
        new_segmentation += " " + labs[index_d]
        index_d+=1 
    while "  " in new_segmentation:
        new_segmentation = new_segmentation.replace("  "," ")
    return new_segmentation

def write_output(f_path, segmentation):
    with codecs.open(f_path,"w", "utf-8") as output_file:
        output_file.write(segmentation + "\n")


def main():
    labs_f = glob.glob(sys.argv[1]+"*")
    seg_folder = sys.argv[2] if sys.argv[2][-1] == "/" else sys.argv[2]+"/"
    output_folder = sys.argv[3] if sys.argv[3][-1] == "/" else sys.argv[3]+"/"

    if labs_f:
        for lab_f in labs_f:
            print(lab_f)
            name = lab_f.split('/')[-1].split(".")[0]
            lab = read_lab(lab_f)
            seg = get_segmentation(seg_folder+name)
            new_seg = merge_silence(seg,lab)
            write_output(output_folder+name+".hs", new_seg)


if __name__ == '__main__':
    main()
