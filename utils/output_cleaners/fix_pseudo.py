import sys
import glob 

def main():
    if len(sys.argv) < 3:
        print "python fix_pseudo.py input_folder/ output_folder/"
        sys.exit(1)

    input_folder = sys.argv[1] if sys.argv[1][-1] == '/' else sys.argv[1] + '/'
    output_folder = sys.argv[2] if sys.argv[2][-1] == '/' else sys.argv[2] + '/'
    paths = glob.glob(input_folder + '*.phn')
    for f in paths:
        with open(f,"r") as inputFile:
            f_name = f.split('/')[-1]
            with open(output_folder + f_name,"w") as outputFile:
                for line in inputFile: #641000 780000 a37
                    line = line.split(" ")
                    outputFile.write("%10.8f %10.8f  %s" %(float(line[0])/1000000, float(line[1])/1000000, line[2]))

if __name__ == '__main__':
    main()
