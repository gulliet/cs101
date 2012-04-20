#!/usr/bin/python

# name = 'feedinformant'
# version = '0.1.0'
# description = 'Unsupervised Machine Learning classifying RSS feeds'
# author = 'Jean-Marc Gulliet'
# author_email = 'jeanmarc.gulliet@gmail.com'
#
# Copyright (C) 2012 Jean-Marc Gulliet. This work is licensed under a 
# Creative Commons Attribution-Noncommercial-Share Alike 3.0 United 
# States License.(CC BY-NC-SA 3.0)
# For more info, see http://creativecommons.org/licenses/by-nc-sa/3.0/
#

import argparse
import codecs
from collections import defaultdict
from math import sqrt
import random
import re
import string
from time import localtime

import feedparser

# list of common words with contractions from the Web site Text Fixer
# http://www.textfixer.com/resources/common-english-words.php
#
COMMON_WORDS = ["'tis", "'twas", 'a', 'able', 'about', 'across', 'after', "ain't", 'all', 'almost', 'also', 'am', 'among', 'an', 'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'but', 'by', 'can', "can't", 'cannot', 'could', "could've", "couldn't", 'dear', 'did', "didn't", 'do', 'does', "doesn't", "don't", 'either', 'else', 'ever', 'every', 'for', 'from', 'get', 'got', 'had', 'has', "hasn't", 'have', 'he', "he'd", "he'll", "he's", 'her', 'hers', 'him', 'his', 'how', "how'd", "how'll", "how's", 'however', 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'just', 'least', 'let', 'like', 'likely', 'may', 'me', 'might', "might've", "mightn't", 'most', 'must', "must've", "mustn't", 'my', 'neither', 'no', 'nor', 'not', 'of', 'off', 'often', 'on', 'only', 'or', 'other', 'our', 'own', 'rather', 'said', 'say', 'says', "shan't", 'she', "she'd", "she'll", "she's", 'should', "should've", "shouldn't", 'since', 'so', 'some', 'than', 'that', "that'll", "that's", 'the', 'their', 'them', 'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'tis', 'to', 'too', 'twas', 'us', 'wants', 'was', "wasn't", 'we', "we'd", "we'll", "we're", 'were', "weren't", 'what', "what'd", "what's", 'when', 'when', "when'd", "when'll", "when's", 'where', "where'd", "where'll", "where's", 'which', 'while', 'who', "who'd", "who'll", "who's", 'whom', 'why', "why'd", "why'll", "why's", 'will', 'with', "won't", 'would', "would've", "wouldn't", 'yet', 'you', "you'd", "you'll", "you're", "you've", 'your']

def get_feeds(db, mode = 'live'):
    try:
        print 'Getting list of', mode, 'feeds...'
        file = open(mode + '_feed_list.txt')
    except IOError, e:
        print 'ERROR: could not open configuration file: ', e
        return -1

    data = file.readlines()
    feeds = []
    for line in data:
        feeds.append(line.strip())
    file.close()
    print 'OK'
    
    feeds_parsed, articles_parsed = update_contents_database(db, feeds)
    print 'Parsed', articles_parsed, 'articles from', feeds_parsed, 'sources' 

def remove_html_tags(data):
    p = re.compile(r'</?[^>]+>')
    return p.sub('', data)

def remove_extra_spaces(data):
    p = re.compile(r'\s+')
    return p.sub(' ', data)

def update_contents_database(db, feeds):
    total_feeds = 0
    total_articles = 0
    for feed in feeds:
        total_feeds += 1
        print '-- Now, parsing', feed
        d = feedparser.parse(feed)        
        parsed = 0
        for entry in d.entries:
            if not entry.has_key('id'):
                break
            parsed += 1
            total_articles += 1
            e_title = ''
            if entry.has_key('title'):
                e_title = remove_extra_spaces(remove_html_tags(entry.title))
            e_descr = ''
            if entry.has_key('description'):
                e_descr = remove_extra_spaces(remove_html_tags(entry.description))
            db[entry.id] = [e_title, e_descr]
        print '  ', parsed, 'articles parsed'
    return total_feeds, total_articles

def discard_punctuation(s):
    # get ride of all punctuations but the single quote character (needed
    # for contraction like "haven't" 
    str = ''
    for c in s:
        if c in string.punctuation and c != "'":
            str = str + ' '
        else:
            str = str + c
    return str

def discard_common_words(words):
    # the index does not take into account words like definite article,
    # conjonction, modals, etc.
    kept = []
    for word in words:
        if len(word) > 2 and word not in COMMON_WORDS:
            kept.append(word)
    return kept

def build_keyword_index(s):
    v = {}
    s = discard_punctuation(s)
    words = s.split()
    words = discard_common_words(words)
    for word in words:
        if word in v:
            v[word] = v[word] + 1.0
        else:
            v[word] = 1.0
    return v

def build_index(contents):
    db = {}
    for feed in contents:
        # processing title + description
        txt = contents[feed][0] + ' ' + contents[feed][1]
        db[feed] = build_keyword_index(txt)
    return db


def pearson_correlation(vec1, vec2):
    """
    >>> pearson_correlation({}, {})
    0.0
    >>> pearson_correlation({'a':3.0}, {'a':3.0})
    1.0
    >>> pearson_correlation({'a':-3.0}, {'a':-3.0})
    1.0
    >>> pearson_correlation({'a':-3.0}, {'b':3.0})
    0.0
    >>> pearson_correlation({'a':-3.0}, {'a':3.0})
    1.0
    >>> pearson_correlation({'a':-3.0, 'b':0.0}, {'a':3.0, 'b':0.0})
    -1.0
    >>> pearson_correlation({'a':0.0, 'b':0.0, 'c':0.0}, {'a':1.0, 'b':2.0, 'c':3.0})
    1.0
    >>> pearson_correlation({'a':3.0, 'b':4.0, 'c':0.0}, {})
    0.0
    >>> pearson_correlation({'a':-3.0, 'b':-4.0, 'c':-0.0}, {})
    0.0
    >>> pearson_correlation({'a':3.0, 'b':-4.0}, {'a':-3.0, 'b':-4.0})
    1.0
    >>> pearson_correlation({'a':-3.0, 'b':-4.0, 'c':0.0}, {'a':0.0, 'b':2.0, 'c':-5.0})
    -0.9992600812897368
    >>> pearson_correlation({'a':2.0, 'b':-3.0, 'c':0.0}, {'a':-1.0, 'e':-2.0, 'f':5.0})
    1.0
    """
    # we take only the keywords common to both entries
    sim = [val for val in vec1 if val in vec2]
    n = len(sim)
    if n == 0:
        return 0.0

    sum1 = 0.0
    sum2 = 0.0
    sum1_sq = 0.0
    sum2_sq = 0.0
    p_sum = 0.0

    for i in sim:
        sum1 += vec1[i]
        sum2 += vec2[i]
        sum1_sq += pow(vec1[i], 2)
        sum2_sq += pow(vec2[i], 2)
        p_sum += (vec1[i] * vec2[i])

    # Computing Pearson score
    numerator = p_sum - (sum1 * sum2 / n)
    denominator = sqrt(abs((sum1_sq - pow(sum1, 2)/n) * (sum2_sq - pow(sum2, 2)/n)))
    if denominator < 10.0**-9:
        return 1.0

    r = numerator / denominator
    
    return r

def pearson_distance(vec1, vec2):
    r = pearson_correlation(vec1, vec2)
    return 1.0 - r

def manhattan_distance(vec1, vec2):
    """
    >>> manhattan_distance({}, {})
    0.0
    >>> manhattan_distance({'a':-3.0}, {'b':3.0})
    6.0
    >>> manhattan_distance({'a':0.0, 'b':0.0, 'c':0.0}, {'a':1.0, 'b':2.0, 'c':3.0})
    6.0
    >>> manhattan_distance({'a':3.0, 'b':4.0, 'c':0.0}, {})
    7.0
    >>> manhattan_distance({'a':-3.0, 'b':-4.0, 'c':-0.0}, {})
    7.0
    >>> manhattan_distance({'a':3.0, 'b':-4.0}, {'a':-3.0, 'b':-4.0})
    6.0
    >>> manhattan_distance({'a':-3.0, 'b':-4.0, 'c':0.0}, {'a':0.0, 'b':2.0, 'c':-5.0})
    14.0
    """
    distance = 0.0
    for key in [val for val in vec1 if val in vec2]:
        distance += abs(vec1[key] - vec2[key])
    for key in [val for val in vec1 if val not in vec2]:
        distance += abs(vec1[key])
    for key in [val for val in vec2 if val not in vec1]:
        distance += abs(vec2[key])
    return distance

def euclidean_distance(vec1, vec2):
    """
    >>> euclidean_distance({}, {})
    0.0
    >>> euclidean_distance({'a':-3.0}, {'b':3.0})
    4.242640687119285
    >>> euclidean_distance({'a':0.0, 'b':0.0, 'c':0.0}, {'a':1.0, 'b':2.0, 'c':3.0})
    3.7416573867739413
    >>> euclidean_distance({'a':3.0, 'b':4.0, 'c':0.0}, {})
    5.0
    >>> euclidean_distance({'a':-3.0, 'b':-4.0, 'c':-0.0}, {})
    5.0
    >>> euclidean_distance({'a':3.0, 'b':-4.0}, {'a':-3.0, 'b':-4.0})
    6.0
    >>> euclidean_distance({'a':-3.0, 'b':-4.0, 'c':0.0}, {'a':0.0, 'b':2.0, 'c':-5.0})
    8.366600265340756
    """
    distance = 0.0
    for key in [val for val in vec1 if val in vec2]:
        distance += pow(vec1[key] - vec2[key], 2)
    for key in [val for val in vec1 if val not in vec2]:
        distance += pow(vec1[key], 2)
    for key in [val for val in vec2 if val not in vec1]:
        distance += pow(vec2[key], 2)
    distance = sqrt(distance)
    return distance

def vector_norm_sq(vec):
    """
    >>> vector_norm_sq({})
    0.0
    >>> vector_norm_sq({'a':-3.0})
    9.0
    >>> vector_norm_sq({'a':0.0, 'b':0.0, 'c':0.0})
    0.0
    >>> vector_norm_sq({'a':3.0, 'b':4.0, 'c':0.0})
    25.0
    >>> vector_norm_sq({'a':-3.0, 'b':4.0, 'c':0.0})
    25.0
    >>> vector_norm_sq({'a':3.0, 'b':-4.0, 'c':0.0})
    25.0
    >>> vector_norm_sq({'a':-3.0, 'b':-4.0, 'c':0.0})
    25.0
    """
    norm_sq = 0.0
    for key in vec:
        norm_sq += pow(vec[key], 2)
    return norm_sq

def vector_norm(vec):
    """
    >>> vector_norm({})
    0.0
    >>> vector_norm({'a':-3.0})
    3.0
    >>> vector_norm({'a':0.0, 'b':0.0, 'c':0.0})
    0.0
    >>> vector_norm({'a':3.0, 'b':4.0, 'c':0.0})
    5.0
    >>> vector_norm({'a':-3.0, 'b':4.0, 'c':0.0})
    5.0
    >>> vector_norm({'a':3.0, 'b':-4.0, 'c':0.0})
    5.0
    >>> vector_norm({'a':-3.0, 'b':-4.0, 'c':0.0})
    5.0
    """
    norm = sqrt(vector_norm_sq(vec))
    return norm

def vector_dot_product(vec1, vec2):
    """
    >>> vector_dot_product({}, {})
    0.0
    >>> vector_dot_product({'a':1.0, 'b':1.0}, {'a':0.0, 'b':0.0})
    0.0
    >>> vector_dot_product({'a':1.0, 'b':1.0}, {})
    0.0
    >>> vector_dot_product({'a':3.0, 'b':0.0}, {'a':0.0, 'b':3})
    0.0
    >>> vector_dot_product({'a':3.0}, {'b':3})
    0.0
    >>> vector_dot_product({'a':3.0}, {'a':3})
    9.0
    >>> vector_dot_product({'a':-3.0}, {'a':3})
    -9.0
    >>> vector_dot_product({'a':2.0, 'b':-3.0, 'c':0.0}, {'a':-1.0, 'b':-2.0, 'c':5.0})
    4.0
    >>> vector_dot_product({'a':2.0, 'b':-3.0, 'c':0.0}, {'a':-1.0, 'e':-2.0, 'f':5.0})
    -2.0
    """
    dot_prod = 0.0
    for key in [val for val in vec1 if val in vec2]:
        dot_prod += (vec1[key] * vec2[key])
    return dot_prod

def cosine_similarity(vec1, vec2):
    """
    >>> cosine_similarity({}, {})
    0.0
    >>> cosine_similarity({'a':1.0, 'b':1.0}, {'a':0.0, 'b':0.0})
    0.0
    >>> cosine_similarity({'a':1.0, 'b':1.0}, {})
    0.0
    >>> cosine_similarity({'a':3.0, 'b':0.0}, {'a':0.0, 'b':3.0})
    0.0
    >>> cosine_similarity({'a':3.0}, {'b':3.0})
    0.0
    >>> cosine_similarity({'a':3.0}, {'a':3.0})
    1.0
    >>> cosine_similarity({'a':-3.0}, {'a':3.0})
    -1.0
    >>> cosine_similarity({'a':2.0, 'b':-3.0, 'c':0.0}, {'a':-1.0, 'b':-2.0, 'c':5.0})
    0.20254787341673333
    >>> cosine_similarity({'a':2.0, 'b':-3.0, 'c':0.0}, {'a':-1.0, 'e':-2.0, 'f':5.0})
    -0.10127393670836667
    """
    vector_cosine = 0.0
    denominator = (vector_norm(vec1) * vector_norm(vec2))
    if denominator:
        vector_cosine = vector_dot_product(vec1, vec2) / denominator
    return vector_cosine

def cosine_distance(vec1, vec2):
    """
    >>> cosine_distance({}, {})
    1.0
    >>> cosine_distance({'a':1.0, 'b':1.0}, {'a':0.0, 'b':0.0})
    1.0
    >>> cosine_distance({'a':1.0, 'b':1.0}, {})
    1.0
    >>> cosine_distance({'a':3.0, 'b':0.0}, {'a':0.0, 'b':3.0})
    1.0
    >>> cosine_distance({'a':3.0}, {'b':3.0})
    1.0
    >>> cosine_distance({'a':3.0}, {'a':3.0})
    0.0
    >>> cosine_distance({'a':-3.0}, {'a':3.0})
    2.0
    >>> cosine_distance({'a':2.0, 'b':-3.0, 'c':0.0}, {'a':-1.0, 'b':-2.0, 'c':5.0})
    0.7974521265832667
    >>> cosine_distance({'a':2.0, 'b':-3.0, 'c':0.0}, {'a':-1.0, 'e':-2.0, 'f':5.0})
    1.1012739367083666
    """
    distance = 1.0 - cosine_similarity(vec1, vec2)
    return distance

def tanimoto_coefficient(vec1, vec2):
    """
    >>> tanimoto_coefficient({}, {})
    0.0
    >>> tanimoto_coefficient({'a':1.0, 'b':1.0}, {'a':0.0, 'b':0.0})
    0.0
    >>> tanimoto_coefficient({'a':1.0, 'b':1.0}, {})
    0.0
    >>> tanimoto_coefficient({'a':3.0, 'b':0.0}, {'a':0.0, 'b':3.0})
    0.0
    >>> tanimoto_coefficient({'a':3.0}, {'b':3.0})
    0.0
    >>> tanimoto_coefficient({'a':3.0}, {'a':3.0})
    1.0
    >>> tanimoto_coefficient({'a':-3.0}, {'a':3.0})
    -0.3333333333333333
    >>> tanimoto_coefficient({'a':2.0, 'b':-3.0, 'c':0.0}, {'a':-1.0, 'b':-2.0, 'c':5.0})
    0.10256410256410256
    >>> tanimoto_coefficient({'a':2.0, 'b':-3.0, 'c':0.0}, {'a':-1.0, 'e':-2.0, 'f':5.0})
    -0.044444444444444446
    """
    coeff = 0.0
    dot_prod = vector_dot_product(vec1, vec2)
    denominator = vector_norm_sq(vec1) + vector_norm_sq(vec2) - dot_prod
    if denominator:
        coeff = dot_prod / denominator
    return coeff

def tanimoto_distance(vec1, vec2):
    return 1.0 - tanimoto_coefficient(vec1, vec2)

def compute_distance(func, vec1, vec2):
    # handle tiny negative floating-point-arithmetic value near zero
    distance = func(vec1, vec2)
    if abs(distance) < 0.00000001:
        distance = 0.0
    return distance

def k_means(data, k = 10, func = pearson_distance, max_iter = 25):
    
    # centroids random initialization
    feeds = data.keys()
    centroids = [data[smpl] for smpl in random.sample(feeds, k)]
    
    print '\nNow, running K-Means Algorithm using', str(func)
    lastmatches = None
    for t in range(max_iter):
        print '-- Iteration %d' % t       
        bestmatches = [[] for i in range(k)]
        
        #looking for the closest centroid to each point
        for j in feeds:
            vec = data[j]
            bestmatch = (0, 999999.0)
            
            for i in range(k):
                dist = compute_distance(func, vec, centroids[i])
                if dist < 0:
                    print '\n*** Negative Distance Encountered! ***\n'
                    return
                if dist < bestmatch[1]:
                    bestmatch = (i, dist)
            bestmatches[bestmatch[0]].append(j)
    
        # if nothing has changed since the last iteration
        if bestmatches == lastmatches:
            break
        lastmatches = bestmatches
        
        centroids = [defaultdict(float) for i in range(k)]
        
        # moving centroids
        for i in range(k):
            len_best = len(bestmatches[i])
            
            if len_best > 0:
                for feed_id in bestmatches[i]:
                    vec = data[feed_id]
                    for m in vec:
                        centroids[i][m] += vec[m]
                        
            for key in centroids[i].keys():   
                centroids[i][key] /= len_best
                if centroids[i][key] < 0.001:
                    del centroids[i][key]

    print 'Done'
    return centroids, bestmatches

def classify_feeds(contents, topics, distance):
    distance_func =  distance + '_distance'
    index = build_index(contents)
    centroids, bestmatches = k_means(index, topics, eval(distance_func), 25)
    return index, centroids, bestmatches

def create_html_file(contents, results):
    file_name = 'readnews.html'
    datetime_stamp = '%4d-%02d-%02d T-%02d-%02d-%02d' % localtime()[:6]
    
    try:
        print '\nSaving results in file', file_name
        file = codecs.open(file_name, 'w+', 'utf-8')
    except IOError, e:
        print 'ERROR: could not open output file', file_name, ':', e
        return -1
    
    file.write('<html>\n')
    file.write('<h1>FeedInformant</h1>\n')
    file.write('<b>' + datetime_stamp +'</b>\n')
    
    i = 0
    for id_list in results:
        i += 1
        file.write('<h2>Category ' + str(i) + '</h2>\n')
        file.write('<ul>\n')
        for feed_id in id_list:
            if string.find(feed_id, 'http://') > -1:
                file.write('<li><a href="' + feed_id + '">' + contents[feed_id][0] + '</a></li>\n')
            else:
                file.write('<li>' + contents[feed_id][0] + '</li>\n')
        file.write('</ul>\n')
    
    file.write('</html>\n')
    file.close()

def main():
    contents = {}
    status = get_feeds(contents, mode)
    if status == -1:
        print '*** Could not get valid contents: nothing to do! ***'
        return   
    ind, cent, bst = classify_feeds(contents, args.cat, args.dist)
    create_html_file(contents, bst)


parser = argparse.ArgumentParser(description = 'AI classifying RSS feeds.')
parser.add_argument('-l', '-L' , '--live', action = 'store_true', default = False,
                    help = 'use live Internet feeds (rather than test data)')
parser.add_argument('-d', '--dist', action = 'store', default = 'tanimoto',
                    help = 'distance to use: manhattan, euclidean, cosine, pearson, tanimoto (default)')
parser.add_argument('-c', '--cat', action = 'store', default = '10',
                    help = 'number of categories to use for classification between 2 and 100 (default: 10)')
parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')

args = parser.parse_args()

mode = 'test'
if args.live:
    mode = 'live'
if args.cat < 2 or args.cat > 100:
    args.cat = 10
if args.dist in ['manhattan', 'euclidean', 'cosine', 'pearson', 'tanimoto']:
    main()
else:
    print 'invalid argument'



#if __name__ == "__main__":
    #import doctest
    #doctest.testmod()


