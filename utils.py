#!/usr/bin/env python

from optparse import OptionParser
import os, logging, re

class Token:
    def __init__(self, word, tag):
        self.word = word
        self.tag = tag

    def __str__(self):
        return "%s/%s" % (self.word, self.tag)

def read_tokens(file):
    f = open(file)
    sentences = []
    for l in f.readlines():
        tokens = l.split()
        sentence = []
        tokens_len = len(tokens)
        i = 0
        for token in tokens:
            i = i+1
            ## split only one time, e.g. pianist|bassoonist\/composer/NN
            try:
                word, tag = token.rsplit('/', 1)

                word = re.sub('http[s]?://(?:[a-z]|[0-9]|[#!$-~_@.&amp;+]|[!*\\(\\),]|(?:%[0-9a-f][0-9a-f]))+', '<url>', word, flags=re.IGNORECASE)
                word = re.sub('^(?:www\.|http.+).+', '<url>', word, flags=re.IGNORECASE)
                #print word
                word = re.sub('^@.+', '<@>', word)
                word = re.sub('^#.+', '<#>', word)
                '''if word.startswith('#') and (i > 5 and i < tokens_len-6):
                    word = word[1:len(word)]
                else:
                    word = re.sub('^#.*', '<#>', word)'''
                word = re.sub(u'(?:[:=;<][oO\-\']?[D\)\]\(\]\\\OpP3]+)', "<emot>", word, flags=re.IGNORECASE)
                word = re.sub('one|two|three|four|five|six|seven|eight|nine|ten|half|twenty|thirty|fifty|sixty|hundred|thousand|dozen|million|billion|trillion', '<num>', word, flags=re.IGNORECASE)
                if any(char.isdigit() for char in word):
                    word = '<num>'
                #word = re.sub('[/!\\.*",?:\-\(\)|\[]+', '<punct>', word)
                word = word.lower();

                if word != '...':
                    word = stem_repetitve_chars(word)
                #print word
            except:
                ## no tag info (test), assign tag UNK
                word, tag = token, "UNK"
            sentence.append(Token(word, tag))
        sentences.append(sentence)
    return sentences

def read_tokens1(file):
    f = open(file)
    sentences = []
    for l in f.readlines():
        tokens = l.split()
        sentence = []
        tokens_len = len(tokens)
        i = 0
        for token in tokens:
            i = i+1
            ## split only one time, e.g. pianist|bassoonist\/composer/NN
            try:
                word, tag = token.rsplit('/', 1)

                word = re.sub('http[s]?://(?:[a-z]|[0-9]|[#!$-~_@.&amp;+]|[!*\\(\\),]|(?:%[0-9a-f][0-9a-f]))+', '<url>', word, flags=re.IGNORECASE)
                word = re.sub('^(?:www\.|http.+).+', '<url>', word, flags=re.IGNORECASE)
                word = re.sub('^@.+', '<@>', word)
                word = re.sub('^#.+', '<#>', word)
                word = re.sub(u'(?:[:=;<][oO\-\']?[D\)\]\(\]\\\OpP3]+)', "<emot>", word, flags=re.IGNORECASE)
                word = re.sub('one|two|three|four|five|six|seven|eight|nine|ten|half|twenty|thirty|fifty|sixty|hundred|thousand|dozen|million|billion|trillion', '<num>', word, flags=re.IGNORECASE)
                word = re.sub('^(?:[0-9]+[,:|.-])*[0-9]+$', '<num>', word)
                try:
                    word = float(word)
                    word = '<num>'
                except:
                    pass
                word = word.lower();
                if word != '...':
                    word = stem_repetitve_chars(word)

                if tag == 'NN' or tag == 'NNS':
                    tag = 'N'
                elif tag == 'NNP' or tag == 'NNPS':
                    tag = '^'
                elif tag in ['WDT', 'DT', 'WP$', 'PRP$'] :
                    tag = 'D'
                elif tag == 'PRP' or tag == 'WP':
                    tag = 'O'
                elif tag.startswith('JJ'):
                    tag = 'A'
                elif tag.startswith('V') or tag == 'MD':
                    tag = 'V'
                elif tag == 'UH':
                    tag = '!'
                elif tag.startswith('R') or tag == 'WRB':
                    tag = 'R'
                elif tag == 'CC':
                    tag = '&'
                else:
                    continue
                #print word
            except:
                ## no tag info (test), assign tag UNK
                word, tag = token, "UNK"
            sentence.append(Token(word, tag))
        sentences.append(sentence)
    return sentences

#like reallyyyyyyyyyy to really
def stem_repetitve_chars(word):
    word_len = len(word)
    prev_c = ''
    count = 0
    new_word = ''
    i = 0
    for c in word:
        i = i + 1
        if c == prev_c:
            count = count + 1
        else:
            if count >= 1 and i < word_len:
                new_word += prev_c * 2
            else:
                new_word += prev_c
            prev_c = c
            count = 0
    new_word += prev_c
    return new_word

def read_tokens_orig(file):
    f = open(file)
    sentences = []
    for l in f.readlines():
        tokens = l.split()
        sentence = []
        tokens_len = len(tokens)
        for token in tokens:
            ## split only one time, e.g. pianist|bassoonist\/composer/NN
            try:
                word, tag = token.rsplit('/', 1)
            except:
                word, tag = token, "UNK"
            sentence.append(Token(word, tag))
        sentences.append(sentence)
    return sentences

def calc_accuracy(gold, system):
    assert len(gold) == len(system), "Gold and system don't have the same number of sentence"
    tags_correct = 0
    num_tags = 0
    for sent_i in range(len(gold)):
        assert len(gold[sent_i]) == len(system[sent_i]), "Different number of token in sentence:\n%s" % gold[sent_i]
        for gold_tok, system_tok in zip(gold[sent_i], system[sent_i]):
            #print gold_tok.word, gold_tok.tag, system_tok.word, system_tok.tag
            if gold_tok.tag == system_tok.tag:
                tags_correct += 1
            else:
                pass
                #print gold_tok.word, gold_tok.tag, system_tok.word, system_tok.tag
            num_tags += 1
    return (tags_correct / float(num_tags)) * 100

if __name__ == "__main__":
    usage = "usage: %prog [options] GOLD SYSTEM"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug", action="store_true",
                      help="turn on debug mode")

    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("Please provide required arguments")

    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    gold = read_tokens(args[0])
    system = read_tokens(args[1])
    accuracy = calc_accuracy(gold, system)
    #print "Accuracy: %s" % accuracy
