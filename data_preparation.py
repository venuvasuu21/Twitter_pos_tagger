from random import shuffle
import math

fh = open('dataset/tweet_test1')
fh1 = open('dataset/tweet_test', mode='w')
sentences = list()
sentence = ""
for line in fh:
    line = line.rstrip()
    if line == "":
        sentence = sentence.rstrip()
        fh1.write(sentence)
        fh1.write('\n')
        sentences.append(sentence)
        sentence = ""
    else:
        words = line.split('\t')
        sentence += words[0] + '/' + words[1]+ ' '
sentences.append(sentence)
fh1.write(sentence)
fh.close()
fh1.close()

'''shuffle(sentences)
num = 0
train = open('dataset/tweet_train', mode='w')
test = open('dataset/tweet_test', mode='w')
while(num < len(sentences)):
    if(num < math.floor(len(sentences)*0.8)):
        train.write(sentences[num])
        train.write('\n')
    else:
        test.write(sentences[num])
        test.write('\n')
    num += 1'''




