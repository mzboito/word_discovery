'''
The input for this script should be a segmented corpus. We cannot consider every char a phoneme, since there are some encodings such as X_ tS to represent some sunds.
Solution will be to also feed the unsegmented version of this corpus, this way we have the true set of phones AND the segmentation. 
The output is the aveage token length per sentence and for the whole corpus =)
'''
import sys, codecs

def read_file(f_path):
    return [line.strip().split() for line in codecs.open(f_path,"r","utf-8")]

def match(word, index, phonemes):
    length = 0
    while index < len(phonemes) and phonemes[index] in word:
        #print(phonemes[index], word, len(phonemes[index]))
        word = word[len(phonemes[index]):]
        length+=1
        index+=1
    return index, length

def count_tokens(segmentation, phonemes):
    index = 0
    count = 0
    sum_length = 0
    #print(phonemes)
    for word in segmentation:
        index, length = match(word,index, phonemes)
        #print(word,index, length)
        count+=1
        sum_length+= length
    #print(count)
    return count, sum_length


def process():
    segmentation = read_file(sys.argv[1])
    unsegmented = read_file(sys.argv[2])

    assert len(segmentation) == len(unsegmented)

    sum_tokens = 0.0
    sum_length = 0.0
    num_sentences = len(segmentation) 
    for i in range(num_sentences):
        count, length = count_tokens(segmentation[i], unsegmented[i])
        sum_tokens+= count
        sum_length+= length
        #break
    
    #print(sum_tokens, sum_length)
    average = sum_tokens/num_sentences
    print("Average tokens per sentence")
    print(average)
    average = sum_length/sum_tokens
    print("Average token length")
    print(average)


if __name__ == "__main__":
    process()