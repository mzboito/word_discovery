# Unsupervised Word Discovery Using Encoder-Decoder Neural Machine Translation Models

This repository is passing through heavy changes. :)


# visualization folder

On this folder we have a python script for parsing the log file generated during training by the seq2seq and an r script to generate images for loss and bleu score behavior during training. There is an example file of the log format, called "example.txt"

1) python logFileParser.py example.txt (generates a file called "FILE-NAME.out")

2) Rscript --vanilla createGraphics.r example.out IMAGES-PATH (generates "lossPlot.png" and "bleuPlot.png", it needs ggplot2)



# Reference:

Marcely Zanon Boito,  Laurent Besacier,  and Aline Villavicencio. **Unsupervised worddiscovery using attentional encoder-decoder models**.   In WiNLP (Women and Underrepresented Minorities in Natural Language Processing) Workshop ACL 2017, Vancouver, Canada.

Marcely Zanon Boito, Aléxandre Berard, Laurent Besacier and Aline Villavicencio. **Unwritten Languages Demand Attention Too! Word Discovery with Encoder-Decoder Models**, In ASRU (Automatic Speech Recognition and Undestanding), IEEE Workshop 2017, Okinawa, Japan.
