import sys, glob
from entropy_gen import Corpus


runs = 5
key_run = "run"
versions = ["true", "pseudo"]


def wrapper():
    root_directory = sys.argv[1]
    matrices =  sys.argv[2]
    CORPUS = dict()
    for version in versions:
        CORPUS[version] = dict()
        global runs
        for i in range(runs):
            run_string = key_run + str(i+1)
            path = "/".join([root_directory, version + "_phones", run_string, matrices]) 
            print(path)
            matrices_path = glob.glob(path +"/*")
            c = Corpus(matrices_path, True, None)
            CORPUS[version][run_string] = c.get_average()

    with open(sys.argv[3] + ".csv","w") as output_file:
        runs_s = ["run" + str(i+1) for i in range(runs)]
        output_file.write("\t" + "\t".join(runs_s)+ "\n")
        for key in versions:
            lst = [str(CORPUS[key][run]) for run in runs_s]
            output_file.write("\t".join([key] + lst)+ "\n")




if __name__ == "__main__":
    wrapper()