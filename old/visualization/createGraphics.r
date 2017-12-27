

library("ggplot2")
loss = read.csv("logout",header=FALSE,sep="\t")

lossPlot  = ggplot(data=loss ,aes(x = loss$V1)) + geom_line(aes(y=loss$V4, colour= "Dev")) + geom_line(aes(y=loss$V5, colour= "Train")) + labs(title = "LOSS BEHAVIOR",x="Steps",y="Loss") + scale_colour_manual("Legend",breaks=c("Dev","Train"),values=c(Dev = "blue", Train = "black")) + scale_y_continuous(breaks = round(seq(min(loss$V5), max(loss$V4), by = 20),1))
lossPlot
ggsave(file="lossPlot.png", width = 7.0, height = 3.5)



scoresPlot = ggplot(data=loss, aes(x=loss$V1)) + geom_line(aes(y=loss$V2, colour = "Dev")) + geom_line(aes(y=loss$V3, colour = "Train")) + labs(title = "BLEU SCORE",x="Steps",y="Score") +scale_colour_manual("Legend",breaks=c("Dev","Train"),values=c(Dev = "blue", Train = "black")) + scale_y_continuous(breaks = round(seq(min(loss$V2), max(loss$V3), by = 5),1))
scoresPlot

ggsave(file="bleuPlot.png", width = 7.0, height = 3.5)

#step, devScore, trainScore, devLoss, trainLoss