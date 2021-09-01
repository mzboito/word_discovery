import codecs
import sys


def main():
    
    dpseg_out_path = sys.argv[1]
    segmentation_path = sys.argv[2]
    output_file = sys.argv[3]

    dpseg_out = [line for line in codecs.open(dpseg_out_path, "r", "UTF-8", errors="replace")] #dpseg out file introduces char errors
    segmentation = [line for line in codecs.open(segmentation_path, "r", "UTF-8")] #.replace(" ","")


    flag = False
    dpseg_clean =[]
    #print(dpseg_out)
    for i in range(len(dpseg_out)):
        #print(dpseg_out[i])
        if u'_nstrings=xxx\n' == dpseg_out[i]:
            #print(dpseg_out[i],i)
            break
        if flag:
            dpseg_clean.append(dpseg_out[i])
            #print(dpseg_out[i])
        if "State:" in dpseg_out[i]:
            #print(dpseg_out[i],i)
            flag = True

    #segmentation: a20 a31 a37 a31 
    print(len(dpseg_clean))
    #print(dpseg_clean[33185:])
    print(len(segmentation))
    assert len(dpseg_clean) == len(segmentation)

    for j in range(len(segmentation)):
        line = segmentation[j].split(" ")
        dpseg_line = dpseg_clean[j]
        index = 0
        new_line = ""
        for i in range(len(line)):
            #print(dpseg_line,index)
            #print(new_line)
            if dpseg_line[index] == " ": #if found a boundary
                new_line += " "
                index+=1
            new_line += line[i] #adds the characters
            index+=1
        segmentation[j] = new_line


    with codecs.open(output_file, "w", "UTF-8") as output:
        for line in segmentation:
            output.write(line)


if __name__ == '__main__':
    main()
