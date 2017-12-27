
import sys



infos = []

lines = []

with open(sys.argv[1], "r") as logFile:
    for line in logFile:
        lines.append(line)



for i in range(0, len(lines)):
    if "main step" in lines[i]:
        step = lines[i].split(" ")[4]
        devLoss = lines[i].strip("\n").split(" ")[-1]
        #trainLoss = lines[i+2].strip("\n").split(" ")[-1]
        if "creating directory" in lines[i+3]:
            devScore = lines[i+7].split(" ")[3].replace("score=","")
            trainScore = lines[i+8].split(" ")[3].replace("score=","")
        else:
            devScore = lines[i+6].split(" ")[3].replace("score=","")
            trainScore = lines[i+7].split(" ")[3].replace("score=","")
        infos.append([step, devScore, trainScore, devLoss])
    else:
        pass


with open(sys.argv[1].replace(".txt","out"),"w") as outputFile:
    for i in range(0,len(infos)):
        outputFile.write("\t".join(infos[i]) + "\n")


'''
0 03/16 16:25:49 main step 1500 epoch 11 learning rate 0.5000 step-time 0.0899 loss 44.1231
1 03/16 16:25:50   eval: loss 46.17
2 03/16 16:25:57   eval: loss 32.82
3 03/16 16:25:57 creating directory ../experiments/T7/model/checkpoints
4 03/16 16:25:57 saving model to ../experiments/T7/model/checkpoints
5 03/16 16:25:57 finished saving model
6 03/16 16:25:57 starting decoding
7 03/16 16:25:59 main score=1.22 penalty=0.833 ratio=0.846
8 03/16 16:26:15 main score=1.59 penalty=0.866 ratio=0.874

0 03/16 17:16:48 main step 30000 epoch 207 learning rate 0.5000 step-time 0.0897 loss 5.3593
1 03/16 17:16:49   eval: loss 84.44
3 03/16 17:16:56   eval: loss 4.84
4 03/16 17:16:56 saving model to ../experiments/T7/model/checkpoints
5 03/16 17:16:56 finished saving model
6 03/16 17:16:56 starting decoding
7 03/16 17:16:58 main score=20.28 penalty=0.950 ratio=0.951
8 03/16 17:17:14 main score=81.75 penalty=0.978 ratio=0.978
9 03/16 17:17:14 finished training
'''
