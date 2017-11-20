from django.test import TestCase
import fyp_webapp.TwitterProcessing.termsfrequency as termsfrequency
from fyp_webapp.TwitterProcessing import termsfrequency
import fyp_webapp.ElasticSearch.elastic_utils as es
import time

class TestTermsFrequency(TestCase):

    def setUp(self):
        es.create_index("test")

    def tearDown(self):
        es.delete_index("test")

    def test_execute_all(self):
        doc = {"text": "test more than one word. test"}
        res = es.add_entry(index_name="test", id=1, body=doc)
        time.sleep(2)
        result = termsfrequency.execute_all_term_functions(self, index="test")
        self.assertEqual(7, result["max_sentence_size"])
