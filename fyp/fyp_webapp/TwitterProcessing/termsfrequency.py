import json
from collections import Counter
from .preprocessor import Preprocessor
import nltk
import string

#TODO Add docs

class TermFrequency:
    def __init__(self):
        stopwords = nltk.download('stopwords')

        self.punctuation = list(string.punctuation)
        self.stop = stopwords.words('english') + self.punctuation + ['rt', 'via', '…', 'I', '’', 'The', '!']

    def max_tweet_sentence_size(self,filename):
        #TODO need to add new function to support elasticsearch first
        return -1

    def count_word_frequency(self, filename):
        #TODO need to add new function to support elasticsearch first
        return -1

    def most_common_words(self, num_results, filename):
        #TODO need to add new function to support elasticsearch first
        return -1










