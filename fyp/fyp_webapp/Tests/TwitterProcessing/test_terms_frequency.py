from django.test import TestCase
import fyp_webapp.TwitterProcessing.termsfrequency as termsfrequency
from fyp_webapp.TwitterProcessing.termsfrequency import TermFrequency as terms

class TestTermsFrequency(TestCase):

    #setup
   # def setUp(self):


    #teardown

    def test_max_tweet_sentence_size(self):
        self.assertEqual(-1, terms.max_tweet_sentence_size(self, "test"))