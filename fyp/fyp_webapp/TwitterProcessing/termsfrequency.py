import json
from collections import Counter
from fyp_webapp.TwitterProcessing import preprocessor
import nltk
import string
from fyp_webapp.ElasticSearch import elastic_utils as es
from nltk.corpus import stopwords


#TODO Add docs



nltk.download('stopwords')

punctuation = list(string.punctuation)
stop = stopwords.words('english') + punctuation + ['rt', 'via', '…', 'I', '’', 'The', '!']

def count_words(data, number_word_frequency_results=40):
    current_max_sentence_size = 0
    count_word_frequency = Counter()
    for entry in data:
        print (entry)
        terms_all = [term for term in entry]
        count_word_frequency.update(terms_all)
    return count_word_frequency.most_common(number_word_frequency_results)

#In a realistic sense. These should all be done together.
def execute_all_term_functions(self, index, number_word_frequency_results=10):
    current_max_sentence_size = 0
    count_word_frequency = Counter()
    res = es.iterate_search(index_name=index)
    for entry in res:
        #Step 1. Get the max sentence size as we go.
        print (entry)
        current_tweet = preprocessor.preprocess(entry['_source']['text'])
        if (len(current_tweet) > current_max_sentence_size):
            current_max_sentence_size = len(current_tweet)

        #Step 2. Count the number of words in the frequency.
        terms_all = [term for term in preprocessor.preprocess(entry['_source']['text']) if term not in stop]
        # Update the counter
        count_word_frequency.update(terms_all)
    dict = {"word_frequency": count_word_frequency.most_common(number_word_frequency_results),
                                                                   "max_sentence_size": current_max_sentence_size}
    return dict


    def max_tweet_sentence_size(self,filename):
        #TODO need to add new function to support elasticsearch first
        return -1

    def count_word_frequency(self, filename):
        return -1

    def most_common_words(self, num_results, filename):
        #TODO need to add new function to support elasticsearch first
        return -1










