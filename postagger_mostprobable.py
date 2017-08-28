#!/usr/bin/env python

from optparse import OptionParser
import os, logging
import utils
import collections
import operator
import time

def create_model(sentences):
    model = None
    tags = collections.defaultdict(lambda: collections.defaultdict(int))
    tokens = collections.defaultdict(lambda: collections.defaultdict(int))
    lasttag = '<s>'
    ## YOUR CODE GOES HERE: create a model
    for sentence in sentences:
        lasttag = '<s>'
        for token in sentence:
            tags[lasttag][token.tag] +=1 ;
            tokens[token.tag][token.word] += 1
            lasttag = token.tag
    model = (tags, tokens)
    return model

def predict_tags(sentences, model):
    ## YOU CODE GOES HERE: use the model to predict tags for sentences
    tokens = model[1]
    tags = model[0]
    for sentence in sentences:
        for token in sentence:
            temp_count = 0
            try:
                token.tag = max([(tokens[tag][token.word],tag) for tag in tags])[1]
            except:
                token.tag = 'N'
    return sentences

if __name__ == "__main__":
    start = time.time()
    usage = "usage: %prog [options] GOLD TEST"
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

    training_file = args[0]
    training_sents = utils.read_tokens(training_file)
    test_file = args[1]
    test_sents = utils.read_tokens(test_file)

    model = create_model(training_sents)

    ## read sentences again because predict_tags(...) rewrites the tags
    sents = utils.read_tokens(training_file)
    predictions = predict_tags(sents, model)
    accuracy = utils.calc_accuracy(training_sents, predictions)
    print "Accuracy in training [%s sentences]: %s" % (len(sents), accuracy)

    ## read sentences again because predict_tags(...) rewrites the tags
    sents = utils.read_tokens(test_file)
    predictions = predict_tags(sents, model)
    accuracy = utils.calc_accuracy(test_sents, predictions)
    print "Accuracy in testing [%s sentences]: %s" % (len(sents), accuracy)

    end = time.time()

