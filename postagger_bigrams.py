#!/usr/bin/env python

from optparse import OptionParser
import logging
import utils
import collections
import time

words_in_train = collections.defaultdict(int)
tag_given_word_all_sent = collections.defaultdict(lambda: collections.defaultdict(int))

def create_model(sentences):
    model = None
    tags = collections.defaultdict(lambda: collections.defaultdict(int))
    tokens = collections.defaultdict(lambda: collections.defaultdict(int))
    single_tags = collections.defaultdict(int)
    lasttag = '<s>'
    for sentence in sentences:
        lasttag = '<s>'
        for token in sentence:
            words_in_train[token.word] += 1
            tags[lasttag][token.tag] += 1
            tokens[token.tag][token.word] += 1
            single_tags[token.tag] += 1
            lasttag = token.tag
    # Calculating probabilities
    for (lastTag, dict_tags) in tags.items():
        sum_last_tag_values = sum(tags[lastTag].values())
        for presentTag in dict_tags:
            tags[lastTag][presentTag] = float(tags[lastTag][presentTag]) / (sum_last_tag_values)
    for (word_tag, dict_words) in tokens.items():
        sum_word_tag_values = sum(tokens[word_tag].values())
        for word in dict_words:
            tokens[word_tag][word] = float(tokens[word_tag][word]) / (sum_word_tag_values)

    sum_all_tags = sum(single_tags.values())
    for tag in single_tags:
        single_tags[tag] = float(single_tags[tag]) / sum_all_tags

    model = (tags, tokens, single_tags)
    #print "Tokens in training are ", sum(words_in_train.values())
    return model

def prob_unknown_word(sentences):
    unknown_word_count = 0
    word_count = 0
    for sentence in sentences:
        for token in sentence:
            word_count += 1
            if token.word not in words_in_train:
                unknown_word_count += 1
    #print "unknown Tokens in validation are ", unknown_word_count, word_count
    return float(unknown_word_count) / (unknown_word_count+sum(words_in_train.values()))

def morphological_rules(token_tags, single_tags, word):
    prob_unknown_word = 0.0907394738479 / 1459
    if word in tag_given_word_all_sent:
        for tag, prob in tag_given_word_all_sent.get(word).items():
            token_tags[tag][word] = (prob * prob_unknown_word) / single_tags[tag]
    else:
        if word.endswith('\'s'):
            token_tags['S'][word] = (0.3 * prob_unknown_word) / single_tags['S']
            token_tags['Z'][word] = (0.3 * prob_unknown_word) / single_tags['Z']
            token_tags['L'][word] = (0.2 * prob_unknown_word) / single_tags['L']
            token_tags['N'][word] = (0.1 * prob_unknown_word) / single_tags['N']
            token_tags['^'][word] = (0.1 * prob_unknown_word) / single_tags['^']
        elif word.endswith('ly'):
            token_tags['A'][word] = (0.20 * prob_unknown_word) / single_tags['A']
            token_tags['R'][word] = (0.70 * prob_unknown_word) / single_tags['R']
            token_tags['V'][word] = (0.05 * prob_unknown_word) / single_tags['V']
            token_tags['G'][word] = (0.05 * prob_unknown_word) / single_tags['G']
        elif word.endswith('ing'):
            token_tags['N'][word] = (0.2 * prob_unknown_word) / single_tags['N']
            token_tags['V'][word] = (0.7 * prob_unknown_word) / single_tags['V']
            token_tags['A'][word] = (0.1 * prob_unknown_word) / single_tags['A']
        elif word.endswith('ed'):
            token_tags['N'][word] = (0.1 * prob_unknown_word) / single_tags['N']
            token_tags['V'][word] = (0.5 * prob_unknown_word) / single_tags['V']
            token_tags['A'][word] = (0.4 * prob_unknown_word) / single_tags['A']
        else:
            token_tags['N'][word] = (0.5 * prob_unknown_word) / single_tags['N']
            token_tags['V'][word] = (0.1 * prob_unknown_word) / single_tags['V']
            token_tags['^'][word] = (0.4 * prob_unknown_word) / single_tags['^']

def predict_tags(sentences, model):
    # Viterbi algorithm
    token_tags = model[1]
    tags_prob = model[0]
    single_tags = model[2]
    tags_array = token_tags.keys()
    most_probable_tag = max([(single_tags[tag],tag) for tag in single_tags])[1]
    #print most_probable_tag
    for sentence in sentences:
        viterbi_mat = collections.defaultdict(lambda: collections.defaultdict(int))
        # sentence = sents[0]
        sentence_array = [token.word for token in sentence]
        if sentence_array[0] not in words_in_train:
            word = sentence_array[0]
            morphological_rules(token_tags, single_tags, word)
        for idx, tag in enumerate(tags_array):
            viterbi_mat[idx][0] = (tags_prob['<s>'][tag] * token_tags[tag][sentence_array[0]], -1)

        # Enumerating for each word
        for w_idx, word in enumerate(sentence_array):
            if word not in words_in_train:
                morphological_rules(token_tags, single_tags, word)
            if (w_idx == 0): continue
            # Enumerating for each tag
            for t_idx, tag in enumerate(tags_array):
                # [(viterbi_mat[in_t_idx][w_idx-1])[0] * token_tags[tag][word] * tags_prob[in_tag][tag] for in_t_idx, in_tag in enumerate(tags_array)]
                arg_max = 0
                max_val = 0
                for in_t_idx, in_tag in enumerate(tags_array):
                    # in_prob = (viterbi_mat[in_t_idx][w_idx-1])[0] * (float(token_tags[tag][word])/sum((token_tags[tag]).values())) * (float(tags_prob[in_tag][tag])/sum((tags_prob[in_tag]).values()))
                    in_prob = (viterbi_mat[in_t_idx][w_idx - 1])[0] * (
                        token_tags[tag][word] * (tags_prob[in_tag][tag]))
                    if in_prob > max_val:
                        max_val = in_prob
                        arg_max = in_t_idx
                viterbi_mat[t_idx][w_idx] = (max_val, arg_max)  # tags_array[arg_max])
                # break;
        # Finding the sequence by backtracking
        final_vcell = max([(viterbi_mat[i][len(sentence_array) - 1], i) for i in xrange(len(tags_array))])
        last_tag = final_vcell[1]
        prev_tag = final_vcell[0][1]
        for token_idx, token in reversed(list(enumerate(sentence))):
            if token_idx == len(sentence) - 1:
                token.tag = tags_array[last_tag]
                # print token.word, token.tag, tags_array[last_tag]
                continue
            # print token.word,token.tag, tags_array[prev_tag]
            token.tag = tags_array[prev_tag]
            prev_tag = (viterbi_mat[prev_tag][token_idx])[1]

    return sentences

def create_model_all_sent(sentences):
    for sentence in sentences:
        for token in sentence:
            tag_given_word_all_sent[token.word][token.tag] += 1

    for (word, dict_tags) in tag_given_word_all_sent.items():
        sum_word_tag_values = sum(tag_given_word_all_sent[word].values())
        for tag in dict_tags:
            tag_given_word_all_sent[word][tag] = float(tag_given_word_all_sent[word][tag]) / (sum_word_tag_values)

if __name__ == "__main__":

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

	start = time.time()
	print "Creating Model, takes few secs.."
    all_train_sent = utils.read_tokens1('dataset/all_sent')
    create_model_all_sent(all_train_sent)

    training_file = args[0]
    training_sents = utils.read_tokens(training_file)
    test_file = args[1]
    test_sents = utils.read_tokens_orig(test_file)
    model = create_model(training_sents)
    end = time.time()
    print "Model created in %d secs" % (end-start)
	## read sentences again because predict_tags(...) rewrites the tags

    start = time.time()
    print "\nTagging training sentences.."
    sents = utils.read_tokens(training_file)
    predictions = predict_tags(sents, model)
    training_sents_orig = utils.read_tokens_orig(training_file)
    accuracy = utils.calc_accuracy(training_sents_orig, predictions)
    print "Accuracy in training [%s sentences]: %s" % (len(sents), accuracy)
    end = time.time()
    print "Time took to tag %.2f secs" % (float(end - start))

    ## read sentences again because predict_tags(...) rewrites the tags
    start = time.time()
    print "\nTagging testing sentences.."
    sents = utils.read_tokens(test_file)
    #print prob_unknown_word(sents)
    predictions = predict_tags(sents, model)
    accuracy = utils.calc_accuracy(test_sents, predictions)
    print "Accuracy in testing [%s sentences]: %s" % (len(sents), accuracy)

    end = time.time()
    print "Took %.2f secs" % (float(end - start))