import sys, glob
import shutil

path = [line.strip() for line in open("best_entropy","r")][0]
files = glob.glob(path)
#print(path)
#print(files)
for f_path in files:
    #print(f_path)
    shutil.copy2(f_path, 'filtered/') 
