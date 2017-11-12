from datetime import datetime
from elasticsearch import Elasticsearch

es_host = {"host" : "localhost", "port" : 9200}
es = Elasticsearch(hosts=[es_host])

"""Creates an elastic search index. Reads in name as a parameter and outputs if it fails or not."""
def create_index(name):
    # create ES client, create index

    if es.indices.exists(name):
        print ("Index already exists!")
    else:
        print("creating '%s' index..." % (name))
        res = es.indices.create(index=name)
        print(" response: '%s'" % (res))


"""Deletes an elasticsearch index. Reads in name as a parameter."""
def delete_index(name):
    if es.indices.exists(name):
        print("Deleting '%s index..." % name)
        res = es.indices.delete(index=name)
        print (" response: %s'" % (res))
    else:
        print("Index does not exist!")

"""Lists all current existing indexes."""
def list_all_indexes():
    res = es.indices.get_alias("*")
    print (" response: %s" % (res))

"""Create an entry into an existing index. Uses a unique ID to identify. Body is the data entry in question"""
def add_entry(index_name, id, body):
    res = es.index(index=index_name, doc_type="tweet", id=id, body=body)
    if (res['created'] == False):
        print (" Something went wrong! Does an entry with the ID already exist?")


