import numpy as np
import os
import string
import io
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.cluster import KMeans
from fyp_webapp.TwitterProcessing import preprocessor
from fyp_webapp.ElasticSearch import elastic_utils
import time
from fyp_webapp import config as cfg
import pickle


def run_tf_idf(n_clusters, n_init, verbose):
    max_features = 10000


    # Create TF-IDF of texts
    tfidf = TfidfVectorizer(max_df=0.95, min_df=2, stop_words='english', max_features=max_features)
    texts = []
    res = elastic_utils.iterate_search(index_name=cfg.twitter_credentials['topic'])
    for i in res:
        texts.append(i['_source']['text'])

    tfidf_vector = tfidf.fit_transform(texts)

    km=KMeans(n_clusters=2, init='k-means++',n_init=100, verbose=1)
    km.fit(tfidf_vector)
    result = {"model": km, "texts": texts}
    pickle.dump(result, open("save.p", "wb"))
    return result
