from django.test import TestCase

from fyp.fyp_webapp.ElasticSearch import elastic_utils as es

class ElasticUtilsTest(TestCase):
    def setUp(self):
        es.create_index("test")

    def test_create_index(self):
        self.assertEqual(es.create_index("testcase"), " response: ") #An index is made