import sys
import codecs
from random import shuffle

dev = 514
train = 4616
sentences = []

#french
with codecs.open(sys.argv[1],"r","UTF-8") as frenchInput:
  with codecs.open(sys.argv[2],"r","UTF-8") as mboshiInput:
      with codecs.open(sys.argv[3],"r","UTF-8") as listInput:
          for i in range(0,(dev+train)):
              sentences.append([frenchInput.readline(), mboshiInput.readline(), listInput.readline()])


for i in range(0,5):
  with codecs.open("dev.rand"+str(i+1)+".fr","w","UTF-8") as frDevFile:
    with codecs.open("dev.rand"+str(i+1)+".ph","w","UTF-8") as mbDevFile:
        with codecs.open("dev.rand"+str(i+1)+".list","w","UTF-8") as listDevFile:
            with codecs.open("train.rand"+str(i+1)+".fr","w","UTF-8") as frTrainFile:
                with codecs.open("train.rand"+str(i+1)+".ph","w","UTF-8") as mbTrainFile:
                    with codecs.open("train.rand"+str(i+1)+".list","w","UTF-8") as listTrainFile:
                      shuffle(sentences)
                      for i in range(0, len(sentences)):
                          if i < dev:
                              frDevFile.write(sentences[i][0])
                              mbDevFile.write(sentences[i][1])
                              listDevFile.write(sentences[i][2])
                          else:
                              frTrainFile.write(sentences[i][0])
                              mbTrainFile.write(sentences[i][1])
                              listTrainFile.write(sentences[i][2])

