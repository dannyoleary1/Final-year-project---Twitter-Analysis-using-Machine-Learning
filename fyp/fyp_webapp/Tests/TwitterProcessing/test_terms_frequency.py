from django.test import TestCase
import fyp_webapp.TwitterProcessing.termsfrequency as termsfrequency
from fyp_webapp.TwitterProcessing import termsfrequency

class TestTermsFrequency(TestCase):


    def test_execute_all(self):
        res = termsfrequency.execute_all_term_functions(self, index="security")
        print (res["word_frequency"])

    def test_max_tweet_sentence_size(self):
        self.assertEqual(-1, -1)