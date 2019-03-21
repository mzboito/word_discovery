import sys
import glob
import codecs



def main():
    output_folder = sys.argv[2]
    #print(glob.glob(sys.argv[1] + "*"))
    for f_path in glob.glob(sys.argv[1] + "*"):
        f_name = f_path.split("/")[-1]
        with codecs.open(f_path, "r", "utf-8") as input_file:
            with codecs.open(output_folder + "/" + f_name, "w","utf-8") as output_file:
                for line in input_file:
                    #print(line)
                    line = line.replace("\\","").replace("\'", "").replace("-","").replace("[","").replace(".","").replace("]","").replace("`","").replace("#","")
                    output_file.write(line.replace("SIL","").replace(" ",""))




if __name__ == "__main__":
    main()