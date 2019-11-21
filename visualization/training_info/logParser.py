# -*- coding: utf-8 -*-

import sys
import os

class LogParser:
    def __init__(self, log_file, log_out_path, dev_and_train): 
        self.input = log_file
        self.output = log_out_path
        self.data = self.parse(dev_and_train)
    
    def parse(self, dev_and_train):
        if dev_and_train == 1:
            return self.parse_dev()
        elif dev_and_train == 2:
            return self.parse_dev_train()
        else:
            print ("ERROR")
            exit(1)

    def read_file(self):
        return [line for line in open(self.input,"r")]

    def write_out(self):
        with open(self.output,"w") as outputFile:
            if len(self.data[0]) > 3: #has train
                outputFile.write("\t".join(["step","dev_loss", "dev_bleu", "train_loss", "train_bleu\n"]))
            else: #only dev
                outputFile.write("\t".join(["step","dev_loss", "dev_bleu\n"]))
            for line in self.data:
                outputFile.write("\t".join(line) + "\n")

    def parse_dev(self):
        data = []
        lines = self.read_file()
        for i in range(len(lines)):
            if " step " in lines[i]:
                step = lines[i].split(" ")[3]
                i+=2
                dev_score = lines[i].split("dev bleu=")[1].split(" ")[0]
                dev_eval = lines[i].split("loss=")[1].split(" ")[0]
                i+=1
                data.append([step, dev_eval, dev_score])
            else:
                i+=1
        return data

        ''' 
        05/05 10:33:25 step 110000 epoch 215 learning rate 0.001 step-time 0.398 loss 56.197
        05/05 09:26:26 starting evaluation
        05/05 09:26:36 dev bleu=27.52 loss=72.36 penalty=0.929 ratio=0.932
        05/05 09:26:36 saving model to ../NMT_experiments/ENGLISH/exp1/model/checkpoints
        05/05 09:26:37 finished saving model
        '''
    
    def parse_dev_train(self):
        data = []
        lines = self.read_file()
        for i in range(len(lines)):
            if " step " in lines[i]:
                step = lines[i].split(" ")[3]
                i+=2
                dev_score = lines[i].split("dev bleu=")[1].split(" ")[0]
                dev_eval = lines[i].split("loss=")[1].split(" ")[0]
                i+=1
                train_score = lines[i].split("train bleu=")[1].split(" ")[0]
                train_eval = lines[i].split("loss=")[1].split(" ")[0]
                i+=2
                data.append([step, dev_eval, dev_score, train_eval, train_score])
            else:
                i+=1
        return data

        ''' 
        01/20 05:15:48 step 150000 epoch 1040 learning rate 0.001 step-time 0.209 loss 17.447
        01/20 05:15:48 starting evaluation
        01/20 05:15:52 dev bleu=33.40 loss=133.16 penalty=0.982 ratio=0.982
        01/20 05:16:33 train bleu=78.52 loss=6.40 penalty=1.000 ratio=1.004
        01/20 05:16:33 saving model to ../griko_mboshi_exp/FR-MB-FR/exp1/model/checkpoints
        01/20 05:16:33 finished saving model
        '''

def main():
    if len(sys.argv) < 4:
        exit(1)
    else:
        log = LogParser(sys.argv[1], sys.argv[2], int(sys.argv[3]))
        log.write_out()
if __name__ == '__main__':
    main()

