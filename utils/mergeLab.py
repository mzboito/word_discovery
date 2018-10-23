import sys
import glob

SIL_token = "SIL"

def read_lab(file_path):
    labs_dict = dict()
    with open(file_path,"r") as lab:
        for line in lab:
            line = line.split(" ")
            start = float(line[0])
            end = float(line[1])
            symbol = line[2]
            labs_dict[start] = [end, symbol]
    return labs_dict

def read_silence(file_path):
    silence_dict = dict()
    with open(file_path,"r") as lab:
        for line in lab:
            line = line.strip("\n").split(" ")
            symbol = line[2]
            if symbol == SIL_token:
                start = float(line[0])
                end = float(line[1])
                silence_dict[start] = [end, symbol]
    return silence_dict

def get_target(labs_dict, s_start, s_end):
    target = []
    keys = sorted(labs_dict.keys())
    for key in keys:
        if key >= s_start and key <= s_end:
            target.append(key)
        elif key <= s_start and labs_dict[key][0] >= s_start:
            target.append(key)
    return target


def left_adjustment(labs_dict, key, s_start, s_end):
    if key == s_start:
        end = labs_dict[key][0]
        if end == s_end:
            labs_dict[key][1] == SIL_token
        elif end < s_end:
            del labs_dict[key]
            labs_dict[key] = [s_end, SIL_token]
        elif end > s_end:
            content = labs_dict[key]
            labs_dict[key] = [s_end, SIL_token]
            labs_dict[s_end] = content
    elif key < s_start:
        labs_dict[key][0] = s_start
        labs_dict[s_start] = [s_end, SIL_token]
    else:
        print("ERROR AT LEFT ADJUSTMENT")
    return labs_dict

def right_adjustment(labs_dict, key, s_start, s_end):
    end = labs_dict[key][0]
    if end == s_start: #fixed on left adjustment
        return labs_dict
    if end == s_end:
        assert labs_dict[s_start][1] == SIL_token
        del labs_dict[key]
    elif end > s_end: # end < s_end
        content = labs_dict[key]
        del labs_dict[key]
        labs_dict[s_end] = content
    else:
        print("ERROR AT RIGHT ADJUSTMENT")
    return labs_dict

def print_dict(l_dict):
    keys = sorted(l_dict.keys())
    for key in keys:
        print(key, l_dict[key])


def merge(labs_dict, silence_dict, s_key):
    #print_dict(labs_dict)
    s_ending = silence_dict[s_key][0]
    target_keys = get_target(labs_dict, s_key, s_ending)
    #print(target_keys)
    #print(s_key, silence_dict[s_key])
    if len(target_keys) > 2:
        first = target_keys[0]
        last = target_keys[-1]
        for i in range(1,(len(target_keys)-1)):
            #print("deleting stuff")
            #print (target_keys[i])
            del labs_dict[target_keys[i]]
        target_keys = [first, last]
    #print(target_keys)

    if len(target_keys) == 2:
        labs_dict = left_adjustment(labs_dict, target_keys[0], s_key, s_ending)
        labs_dict = right_adjustment(labs_dict, target_keys[1], s_key, s_ending)
    else:
        labs_dict = left_adjustment(labs_dict, target_keys[0], s_key, s_ending)
        labs_dict = right_adjustment(labs_dict, target_keys[0], s_key, s_ending)
    #print_dict(labs_dict)
    #print("\n")
    #sys.exit(1)    
    return labs_dict

def adjust(new_dict):
    pass

def merge_labs(labs_dict, silence_dict):
    for key in sorted(silence_dict.keys()):
        new_dict = merge(labs_dict, silence_dict, key)
    return new_dict

def write_new_lab(new_dict, file_path):
    with open(file_path, "w") as output_folder:
        for key in sorted(new_dict.keys()):
            output_folder.write("{} {} {}\n".format(key, new_dict[key][0], new_dict[key][1]))

def main():
    pseudo_path = glob.glob(sys.argv[1] + "*")
    silence_folder = sys.argv[2]
    output_folder = sys.argv[3]
    for file_path in pseudo_path:
        name = file_path.split("/")[-1]
        labs_dict = read_lab(file_path)
        silence_dict = read_silence(silence_folder + name)
        new_dict = merge_labs(labs_dict, silence_dict)
        write_new_lab(new_dict, output_folder + name)

if __name__ == '__main__':
    main()



'''
example mbn svae lab file
0 400000 a0 -29.125210
400000 1800000 a17 -20.305677
1800000 4500000 a16 -43.997795
4500000 5500000 a45 -21.344807
5500000 6400000 a2 -22.194782
6400000 7200000 a42 -18.548626
7200000 7900000 a47 -18.548674
7900000 8700000 a46 -17.652161
8700000 9000000 a24 -11.334684
9000000 9700000 a13 -11.355268
9700000 10900000 a7 -36.174507
10900000 11700000 a42 -18.572168
11700000 12400000 a24 -18.471512
12400000 13200000 a46 -19.968866
13200000 14600000 a3 -26.819702
14600000 15500000 a42 -15.131303
15500000 17600000 a3 -37.721703
17600000 19000000 a36 -35.624767
19000000 21700000 a39 -40.195095
21700000 27300000 a16 -58.189930
27300000 30300000 a16 -53.702774
30300000 31700000 a39 -27.688293
31700000 32800000 a39 -26.011852
32800000 33200000 a38 -13.639442
'''

'''
same example for true phones
100000 5200000 SIL
5200000 5600000 phn22
5600000 6600000 phn2
6600000 7300000 phn16
7300000 7900000 phn41
7900000 8700000 phn30
8700000 9100000 phn41
9100000 9800000 phn24
9800000 10700000 phn2
10700000 11000000 SIL
11000000 15800000 SIL
15800000 17600000 phn2
17600000 18000000 phn23
18000000 18300000 phn41
18300000 18600000 phn31
18600000 19300000 phn7
19300000 19600000 SIL
19600000 20200000 SIL
20200000 33200000 SIL
'''