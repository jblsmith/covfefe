import json
import re
import numpy as np
import random

# Condense links into a single word;
# Turn ampersands and plus signs into "and";
# Strip all non-alphanumeric characters from words;
# Make some other common replacements.
def clean_word(word):
    original_word = word[:]
    if "http" in word:
        word = "LINK"
    if (word=="&amp;") or (word=="&") or (word=="+"):
        word = "and"
    strip_word = re.sub('[^a-zA-Z0-9\#\@\']',"",word)
    if strip_word=="":
        word = re.sub('-{1,}',"DASH",word)
        word = re.sub('\.{1,}',"ELLIPSIS",word)
        word = re.sub('\/{1,}',"SLASH",word)
        # if word=="":
        #     print original_word
    else:
        word = strip_word
    word = word.strip("'")
    return word

def unclean_word(word, link_list):
    if word=="DASH":
        word = '--'
    elif word=="ELLIPSIS":
        word = "..."
    elif word=='SLASH':
        word = "/"
    elif word=="LINK":
        word = random.choice(link_list)
    return word

def scrape_links(tweets):
    links = []
    for tweet in tweets:
        for word in tweet.split(" "):
            if "http" in word:
                links += [word]
    return links

def collect_ngrams(lower_tweets, n=2):
    valid_tweets = [tweet for tweet in lower_tweets if len(tweet)>=n]
    ngrams = [tweet[i:i+n] for tweet in lower_tweets for i in range(len(tweet)-n)]
    return ngrams

def generate_next_word(grammar, word):
    n_options = len(grammar[word])
    if n_options >= 1:
        return random.choice(grammar[word])
    else:
        return 'STOP'

# Load all the tweets into a list
archive_path = "./trump_tweet_data_archive-master"
tweets = []
for year in range(2009,2018):
    archive = archive_path + "/condensed_" + str(year) + ".json"
    jarch = json.load(open(archive,'r'))
    for tweet in jarch:
        tweets.append(tweet['text'])

# Clean the tweets: strip punctuation, replace punctuation words with words, recognize links, etc.
clean_tweets = [[clean_word(word) for word in ['START']+tweet.lower().split(" ")+['STOP']] for tweet in tweets]
# Some stranded punctuation and emojis get lost in this process... delete them.
clean_tweets = [[word for word in tweet if len(word)>0] for tweet in clean_tweets]
# Pull all the links into a single list:
link_list = scrape_links(tweets)
# Get a rough sense of how long the tweets usually are:
tweet_lengths = [len(tweet) for tweet in clean_tweets if len(tweet)>=6]

# It might be useful to have a flattened list of words and unique vocabulary list:
all_words = [word for tweet in clean_tweets for word in tweet]
vocab = list(set(all_words))

# Collect bigrams:
bigrams = collect_ngrams(clean_tweets, n=2)
# Generate a crudge bigram-based grammar:
bigrammar = {word: [] for word in vocab}
for bg in bigrams:
    bigrammar[bg[0]].append(bg[1])

# Write a new tweet:
def write_new_tweet(grammar, prompt="Despite the constant negative press", tweet_length=18):
    new_tweet = prompt.split(" ")
    word = new_tweet[-1]
    for i in range(len(new_tweet),tweet_length):
        next_word = generate_next_word(grammar, word)
        # print next_word
        new_tweet += [next_word]
        word = next_word
        # If we have randomly landed on the word STOP, end the tweet:
        if (word == "STOP"):
            break
        elif ("STOP" not in grammar[word]):
            a = 1
            # This means that a tweet has never ended on this word, so even if other stop conditions apply, continue.
        elif (word == "") or (len(" ".join(new_tweet))>140):
            break
    return " ".join(new_tweet)

def post_process_tweet(tweet, link_list):
    words = tweet.split(" ")
    # Perform "uncleaning", the opposite of the clean function before, which turns the place-holder word "ELLIPSIS" back into "...", and "LINK" back into a random link, etc.
    new_tweet = " ".join(unclean_word(word, link_list) for word in words if word != "STOP")
    return new_tweet

for j in range(90):
    new_len = random.choice(tweet_lengths)
    # [np.random.randint(len(tweet_lengths))]
    new_tweet = write_new_tweet(bigrammar,"Despite the constant negative press",new_len)
    print post_process_tweet(new_tweet, link_list)
