#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

library("ggplot2")

data = read.csv(args[1],header=TRUE,sep="\t")

print(data$dev_loss)


lossPlot  = ggplot(data=data, aes(x = data$step)) + geom_line(aes(y=data$dev_loss, color = "Dev")) +
    geom_line(aes(y=data$train_loss,color= "Train")) + labs(title = "LOSS BEHAVIOR",x="Steps",y="Loss") + 
    scale_x_continuous(breaks=seq(min(data$step), max(data$step), by = min(data$step)*6), limits = c(0,max(data$step))) 


ggsave(file= paste(args[2],"lossPlot.png"), width = 7.0, height = 3.5)


scoresPlot = ggplot(data=data, aes(x = data$step)) + geom_line(aes(y=data$dev_bleu, color = "Dev")) +
geom_line(aes(y=data$train_bleu,color= "Train")) + labs(title = "BLEU SCORE",x="Steps",y="BLEU") + 
  scale_x_continuous(breaks=seq(min(data$step), max(data$step), by = min(data$step)*6), limits = c(0,max(data$step))) 


ggsave(file= paste(args[2],"bleuPlot.png"), width = 7.0, height = 3.5)

