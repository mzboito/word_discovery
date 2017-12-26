# Unsupervised Word Discovery Using Encoder-Decoder Neural Machine Translation Models

This repository is passing through heavy changes. :)


# visualization folder

For visualizing loss and bleu score behavior during training. There is an example file of the log format, called "example.txt".

1) __python logFileParser.py <FILE-NAME.txt>__ (generates a file called "FILE-NAME.out")

2) __Rscript --vanilla createGraphics.r <FILE-NAME.out> <IMAGES-PATH>__ (generates "lossPlot.png" and "bleuPlot.png", it needs ggplot2)



# Reference:

Marcely Zanon Boito,  Laurent Besacier,  and Aline Villavicencio. **Unsupervised worddiscovery using attentional encoder-decoder models**.   In WiNLP (Women and Underrepresented Minorities in Natural Language Processing) Workshop ACL 2017, Vancouver, Canada.

Marcely Zanon Boito, Aléxandre Berard, Laurent Besacier and Aline Villavicencio. **Unwritten Languages Demand Attention Too! Word Discovery with Encoder-Decoder Models**, In ASRU (Automatic Speech Recognition and Undestanding), IEEE Workshop 2017, Okinawa, Japan.
