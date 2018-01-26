import re
import nltk
import string
from nltk.corpus import stopwords
from nltk.stem.porter import *

#TODO Add docs
#Picks up on the following regex
emoticons_str = r"""
                (?:
                    [:=;] # Eyes
                    [oO\-]? # Nose (optional)
                    [D\)\]\(\]/\\OpP] # Mouth
                )"""

regex_str = [
    emoticons_str,
     r'<[^>]+>',  # HTML tags
     r'(?:@[\w_]+)',  # @-mentions
     r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)",  # hash-tags
     r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',  # URLs

     r'(?:(?:\d+,?)+(?:\.?\d+)?)',  # numbers
     r"(?:[a-z][a-z'\-_]+[a-z])",  # words with - and '
     r'(?:[\w_]+)',  # other words
     r'(?:\S)'  # anything else
]

tokens_re = re.compile(r'(' + '|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE)
emoticon_re = re.compile(r'^' + emoticons_str + '$', re.VERBOSE | re.IGNORECASE)

#Tokenize the data
def tokenize(s):
    return tokens_re.findall(s)

#Process the data
def preprocess(s, lowercase=True):
    tokens = tokenize(s)
    if lowercase:
        tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
    return tokens

def filter_multiple(s, ats=False, hashtags=False, stopwords=False, urls=False, stemming=False):
    entries = preprocess(s)
    if ats:
        entries = remove_ats(entries)
    if hashtags:
        entries = remove_hashtags(entries)
    if stopwords:
        entries = remove_stop_words(entries)
    if urls:
        entries = remove_urls(entries)
    if stemming:
        entries = porter_stemming(entries)
    return entries


def remove_ats(tokens):
    regex_ats = re.compile(r'(?:@[\w_]+)')
    tokens_no_ats = [term for term in tokens if regex_ats.match(term) is None]
    return tokens_no_ats

def remove_hashtags(tokens):
    regex_hashtags = re.compile(r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)")
    tokens_no_hashtags = [term for term in tokens if regex_hashtags.match(term) is None]
    return tokens_no_hashtags

def remove_stop_words(tokens):
    nltk.download('stopwords')

    punctuation = list(string.punctuation)
    stop = stopwords.words('english') + punctuation + ['rt', 'via', '…', 'I', '’', 'The', '!']
    terms_all = [term for term in tokens if term not in stop]
    return terms_all

def remove_urls(tokens):
    regex_urls = re.compile(r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+')
    tokens_no_urls = [term for term in tokens if regex_urls.match(term) is  None]
    return tokens_no_urls

def porter_stemming(tokens):
    stemmer = PorterStemmer()
    singles = [stemmer.stem(plural) for plural in tokens]
    return singles