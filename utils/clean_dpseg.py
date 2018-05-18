import codecs
import sys


def main():
    
    dpseg_out_path = sys.argv[1]
    segmentation_path = sys.argv[2]
    output_file = sys.argv[3]

    dpseg_out = [line for line in codecs.open(dpseg_out_path, "r", "UTF-8", errors="replace")] #dpseg out file introduces char errors
    segmentation = [line.replace(" ","") for line in codecs.open(segmentation_path, "r", "UTF-8")]


    flag = False
    dpseg_clean =[]
    for i in range(len(dpseg_out)):
        if "_nstrings=xxx" in dpseg_out[i]:
            break
        if flag:
            dpseg_clean.append(dpseg_out[i])
        if "State:" in dpseg_out[i]:
            flag = True

    

    assert len(dpseg_clean) == len(segmentation)


    print segmentation[0]
    print dpseg_clean[0]

    for j in range(len(segmentation)):
        line = segmentation[j]
        dpseg_line = dpseg_clean[j]
        index = 0
        new_line = ""
        for i in range(len(line)):
            if dpseg_line[index] == " ": #if found a boundary
                new_line += " "
                index+=1
            new_line += line[i] #adds the characters
            index+=1
        segmentation[j] = new_line
    
    print segmentation[0]
    print dpseg_clean[0]

    with codecs.open(output_file, "w", "UTF-8") as output:
        for line in segmentation:
            output.write(line)


if __name__ == '__main__':
    main()