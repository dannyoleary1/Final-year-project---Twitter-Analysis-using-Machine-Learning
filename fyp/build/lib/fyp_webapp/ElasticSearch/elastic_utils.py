from elasticsearch import Elasticsearch, helpers
import time
import fyp_webapp.config as cfg



#es_host = {"host" : "52.40.244.208", "port" : 9200}
es = Elasticsearch(hosts=[cfg.es_host])

"""Creates an elastic search index. Reads in name as a parameter and outputs if it fails or not."""
def create_index(name):
    # create ES client, create index

    if es.indices.exists(name):
        return ("Index already exists!")
    else:
        res = es.indices.create(index=name)
        return (" response: '%s'" % (res))


"""Deletes an elasticsearch index. Reads in name as a parameter."""
def delete_index(name):
    if es.indices.exists(name):
        res = es.indices.delete(index=name)
        return (" response: %s'" % (res))
    else:
        return("Index does not exist!")

"""Lists all current existing indexes."""
def list_all_indexes():
    res = es.indices.get_alias("*")
    return (" response: %s" % (res))

"""Create an entry into an existing index. Uses a unique ID to identify. Body is the data entry in question"""
def add_entry(index_name, id, body):
    res = es.index(index=index_name, doc_type="tweet", id=id, body=body)
    return res

"""Delete an entry from an existing index. Uses the ID to locate"""
def delete_entry(index_name, id):
    try:
        res = es.delete(index=index_name, doc_type="tweet", id=id)
        return res
    except Exception as e:
        print ("Unexpected error: %s", e)
        return e


"""Allows a search to take place on a given index. Default query or can be changed as an optional parameter"""
def search_index(index_name, query='{"query":{"match_all":{}}}'):
    res = es.search(index=index_name, body=query)
    return res

"""TODO needs to be tested"""
def iterate_search(index_name, query={"query":{"match_all":{}}}):
    res = helpers.scan(
        client=es,
        scroll='2m',
        query=query,
        index=index_name)
    return res

