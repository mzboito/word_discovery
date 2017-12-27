
import sys

def main():
    log_file = sys.argv[1]
    lines = [line for line in open(log_file,"r")]
    infos = []
    for i in range(0, len(lines)):
        if " step " in lines[i]:
            step = lines[i].split(" ")[3]
            i+=1
            dev_eval = lines[i].split("dev eval: loss")[1].strip()
            i+=1
            train_eval = lines[i].split("train eval: loss")[1].strip()
            i+=2
            dev_score = lines[i].split("dev score=")[1].split(" ")[0]
            i+=1
            train_score = lines[i].split("train score=")[1].split(" ")[0]
            i+=3
            infos.append([step, dev_eval, dev_score, train_eval, train_score])
        else:
            i+=1
    with open(sys.argv[1].replace(".txt",".out"),"w") as outputFile:
        outputFile.write("\t".join(["step","dev_loss", "dev_bleu", "train_loss", "train_bleu\n"]))
        for i in range(0,len(infos)):
            outputFile.write("\t".join(infos[i]) + "\n")



if __name__ == '__main__':
    main()

'''
12/07 14:38:47 step 120000 epoch 832 learning rate 0.001 step-time 0.726 loss 46.023
12/07 14:38:59   dev eval: loss 92.84
12/07 14:40:56   train eval: loss 32.01
12/07 14:40:56 starting decoding
12/07 14:41:15 dev score=14.28 penalty=0.962 ratio=0.963
12/07 14:44:08 train score=46.01 penalty=0.978 ratio=0.978
12/07 14:44:08 saving model to ../NAACL/experiments/MFCC_HMM/model/checkpoints
12/07 14:44:08 finished saving model

12/07 16:39:23 step 130000 epoch 902 learning rate 0.001 step-time 0.690 loss 45.755
12/07 16:39:36   dev eval: loss 92.86
12/07 16:41:26   train eval: loss 31.55

12/07 16:41:26 starting decoding
12/07 16:41:44 dev score=14.80 penalty=0.938 ratio=0.940
12/07 16:44:22 train score=46.11 penalty=0.960 ratio=0.961
12/07 16:44:22 saving model to ../NAACL/experiments/MFCC_HMM/model/checkpoints
12/07 16:44:22 finished saving model
12/07 18:33:30 step 140000 epoch 971 learning rate 0.001 step-time 0.653 loss 45.519
12/07 18:33:43   dev eval: loss 93.17
12/07 18:35:39   train eval: loss 31.30
'''
