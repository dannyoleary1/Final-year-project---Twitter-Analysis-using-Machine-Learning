from django.test import TestCase
import fyp_webapp.ElasticSearch.elastic_utils as es

class ElasticUtilsTest(TestCase):
    def setUp(self):
        es.create_index("test")

    def tearDown(self):
        es.delete_index("test")

    def test_create_index(self):
        self.assertIn(" \'index\': \'testcase\'", es.create_index("testcase")) #An index is made
        es.delete_index("testcase")

    def test_delete_index(self):
        self.assertIn("\'acknowledged\': True", es.delete_index("test"))

    def test_list_all_index(self):
        es.create_index("list_all")
        res = es.list_all_indexes()
        self.assertIn("\'test\'" , res)
        self.assertIn("\'list_all\'", res)
        es.delete_index("list_all")
        es.delete_index("test")
        self.assertIn("{}", res)

    def test_add_entry(self):
        doc = {"name": "test"}
        res = es.add_entry(index_name="test", id=1, body=doc)
        self.assertEqual(True, res['created'])
        res = es.add_entry(index_name="test", id=2, body=doc) #This should also work
        self.assertEqual(True, res['created'])
        res = es.add_entry(index_name="test", id=1, body=doc) #This should fail since its the same id
        self.assertEqual(False, res['created'])

    def test_delete_entry(self):
        #Add entry first
        doc = {"name": "test"}
        res = es.add_entry(index_name="test", id=1, body=doc)
        #Now Delete
        res = es.delete_entry(index_name="test", id=1)
        self.assertEqual('deleted', res['result'])
        #Now test when it doesn't exist
        self.assertRaises(Exception, es.delete_entry(index_name="test", id=1))