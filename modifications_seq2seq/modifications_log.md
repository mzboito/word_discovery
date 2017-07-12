List of modifications made from the baseline branch of seq2seq, available at https://github.com/eske/seq2seq.

* In file utils.py:
Addition of the write_attmodel_file function, the last one defined in the file. This function create the .txt matrix files with the soft-alignment probabilities for each sentence.

* In file translation_model.py:
Addition of the line 283 in which I replace the generation of .jpg images by .txt files. By removing the comment symbol from line 282, it is possible to generate both heatmaps and text files.

* In file seq2seq_model.py:
In line 42, in the init function, default temperature is setted for 10.0, instead of 1.0, creating the flatten softmax function described in Duong et al. (2016).