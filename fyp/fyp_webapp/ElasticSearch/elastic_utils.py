from elasticsearch import Elasticsearch, helpers
import time
import fyp_webapp.config as cfg



es = Elasticsearch(hosts=[cfg.es_host])

def create_index(name):
    """Creates an elastic search index.
    @:param name. The name of the index you want to create."""

    # create ES client, create index
    if es.indices.exists(name):
        return ("Index already exists!")
    else:
        res = es.indices.create(index=name)
        return (" response: '%s'" % (res))

def check_index_exists(name):
    """Check if elasticsearch already has an index for a specific name.
    @:param name. The name of the index you want to check."""
    try:
        bool = es.indices.exists(name)
        return bool
    except:
        return False

def delete_index(name):
    """Deletes an ElasticSearch index.
    @:param name. The name of the index you want to delete."""
    if es.indices.exists(name):
        res = es.indices.delete(index=name)
        return (" response: %s'" % (res))
    else:
        return("Index does not exist!")

def list_all_indexes():
    """Lists all indexes that can be found in ElasticSearch."""
    res = es.indices.get_alias("*")
    return (res)

def count_entries(name, body={"query": {"match_all": {}}}):
    """Count the number of entries that are found in a specific ElasticSearch index.
    @:param name. The name of the index you want to count entries for.
    @:param query(optional). The query you want to force on the index. This will return specific results that match the ElasticSearch query you have provided.
    @:return The number of entries that match the specific query."""
    count = es.count(index=name, doc_type="tweet", body=body)
    return count

def add_entry(index_name, id, body):
    """Add a new entry to an existing ElasticSearch index.
    @:param index_name. The name of the index you want to add an entry to.
    @:param id. The ID of the entry (This is incremented by 1 unless it is overwriting something in this particular program, but the function has the ability to add it anywhere.)
    @:param body. This is the data that you want to add as the entry."""
    res = es.index(index=index_name, doc_type="tweet", id=id, body=body)
    return res

def add_entry_median(index_name, body, id=1):
    """Adds the median total to the median-index.
    @:param index_name. This is the name of the median index you want to add to.
    @:param body. The data for the entry.
    @:param id (optional). This is the location in the index that you want to enter this specific entry. It should probably always be one to overwrite the existing one."""
    res = es.index(index=index_name, doc_type="median", id=id, body=body)
    return res

def delete_entry(index_name, id):
    """Delete an entry from an existing ElasticSearch index.
    @:param index_name. The index you want to delete an entry from.
    @:param id. The entries location in that index."""
    try:
        res = es.delete(index=index_name, doc_type="tweet", id=id)
        return res
    except Exception as e:
        print ("Unexpected error: %s", e)
        return e


def search_index(index_name, query='{"que'
                                   'ry":{"match_all":{}}}'):
    """Search an index for specific results.
    @:param index_name. The name of the ElasticSearch index you want to search/query.
    @:param query (optional). The query string you want to use as the query. Default matches everything."""
    res = es.search(index=index_name, body=query)
    return res

def iterate_search(index_name, query={"query":{"match_all":{}}}):
    """Iterate search is a way to search a specific index where everything will not be loaded into memory.
    @:param index_name. The name of the ElasticSearch index you want to search/query.
    @:param query (optional). The query string you want to use as the query. Default matches everything."""
    res = helpers.scan(
        client=es,
        scroll='2m',
        query=query,
        index=index_name)
    return res

def last_id(index_name):
    """Returns the numbeer of entries in the index.
    @:param index_name. The name of the ElasticSearch index."""
    res = search_index(index_name)
    if (res['hits']['total'] is None):
        return 0
    else:
        return res['hits']['total']

def check_for_last_id(index_name, query):
    res = search_index(index_name, query)
    if (res['hits']['total'] == 0):
        return False
    elif (res['hits']['total'] is None):
        return False
    else:
        return True


def last_n_in_index(index_name, number):
    """Returns the last number of results in descending order for an ElasticSearch index.
    @:param index_name. The name of the ElasticSearch index you want to get results for.
    @:param number. The number of results to return."""
    query = {
            "query": {
            "match_all": {}
            },
            "size": number,
            "sort": [
            {
            "_id": {
            "order": "desc"
            }
            }
            ]
        }
    return search_index(index_name, query)

