#!/usr/bin/env Rscript

library("ggplot2")

args = commandArgs(trailingOnly=TRUE)
data = read.csv(args[1],header=TRUE,sep="\t")
out_file = args[2]
train = as.numeric(args[3])

#print(data$dev_loss)

if(train == 2) { #there is train
  lossPlot  = ggplot(data=data, aes(x = data$step)) + geom_line(aes(y=data$dev_loss, color = "Dev")) +
    geom_line(aes(y=data$train_loss,color= "Train")) + labs(title = "LOSS BEHAVIOR",x="Steps",y="Loss", color = "set") + 
    scale_x_continuous(breaks=seq(min(data$step), max(data$step), by = min(data$step)*30), limits = c(0,max(data$step))) +
    coord_cartesian(ylim=c(0,100))
  ggsave(file= paste(out_file,"lossPlot.png"), width = 7.0, height = 3.5)

  scoresPlot = ggplot(data=data, aes(x = data$step)) + geom_line(aes(y=data$dev_bleu, color = "Dev")) +
    geom_line(aes(y=data$train_bleu,color= "Train")) + labs(title = "BLEU SCORE",x="Steps",y="BLEU", color = "set") + 
    scale_x_continuous(breaks=seq(min(data$step), max(data$step), by = min(data$step)*30), limits = c(0,max(data$step))) +
    coord_cartesian(ylim=c(0,100))
  ggsave(file= paste(out_file,"bleuPlot.png"), width = 7.0, height = 3.5)
  
  lossPlot  = ggplot(data=data, aes(x = data$step)) + geom_line(aes(y=data$dev_loss, color = "Dev")) +
    geom_line(aes(y=data$train_loss,color= "Train")) + labs(title = "LOSS BEHAVIOR",x="Steps",y="Loss", color = "set") + 
    scale_x_continuous(breaks=seq(min(data$step), max(data$step), by = min(data$step)*30), limits = c(0,max(data$step))) +
  ggsave(file= paste(out_file,"zoom_lossPlot.png"), width = 7.0, height = 3.5)
  
  scoresPlot = ggplot(data=data, aes(x = data$step)) + geom_line(aes(y=data$dev_bleu, color = "Dev")) +
    geom_line(aes(y=data$train_bleu,color= "Train")) + labs(title = "BLEU SCORE",x="Steps",y="BLEU", color = "set") + 
    scale_x_continuous(breaks=seq(min(data$step), max(data$step), by = min(data$step)*30), limits = c(0,max(data$step))) +
  ggsave(file= paste(out_file,"zoom_bleuPlot.png"), width = 7.0, height = 3.5)

}else { #only dev

  lossPlot  = ggplot(data=data, aes(x = data$step)) + geom_line(aes(y=data$dev_loss, color = "Dev")) +
    labs(title = "LOSS BEHAVIOR",x="Steps",y="Loss", color = "set") + 
    scale_x_continuous(breaks=seq(min(data$step), max(data$step), by = min(data$step)*30), limits = c(0,max(data$step))) +
    coord_cartesian(ylim=c(0,100))
  ggsave(file= paste(out_file,"lossPlot.png"), width = 7.0, height = 3.5)

  scoresPlot = ggplot(data=data, aes(x = data$step)) + geom_line(aes(y=data$dev_bleu, color = "Dev")) +
    labs(title = "BLEU SCORE",x="Steps",y="BLEU", color = "set") + 
    scale_x_continuous(breaks=seq(min(data$step), max(data$step), by = min(data$step)*30), limits = c(0,max(data$step))) +
    coord_cartesian(ylim=c(0,100))
  ggsave(file= paste(out_file,"bleuPlot.png"), width = 7.0, height = 3.5)
  
  lossPlot  = ggplot(data=data, aes(x = data$step)) + geom_line(aes(y=data$dev_loss, color = "Dev")) +
    labs(title = "LOSS BEHAVIOR",x="Steps",y="Loss", color = "set") + 
    scale_x_continuous(breaks=seq(min(data$step), max(data$step), by = min(data$step)*30), limits = c(0,max(data$step)))
  ggsave(file= paste(out_file,"zoom_lossPlot.png"), width = 7.0, height = 3.5)
  
  scoresPlot = ggplot(data=data, aes(x = data$step)) + geom_line(aes(y=data$dev_bleu, color = "Dev")) +
    labs(title = "BLEU SCORE",x="Steps",y="BLEU", color = "set") + 
    scale_x_continuous(breaks=seq(min(data$step), max(data$step), by = min(data$step)*30), limits = c(0,max(data$step)))
  ggsave(file= paste(out_file,"zoom_bleuPlot.png"), width = 7.0, height = 3.5)


}


