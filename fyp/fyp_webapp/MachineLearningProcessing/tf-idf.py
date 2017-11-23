import tensorflow as tf
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


batch_size = 500
max_features = 10000

# Create TF-IDF of texts
tfidf = TfidfVectorizer(max_df=0.95, min_df=2, stop_words='english', max_features=max_features)
texts = []
res = elastic_utils.iterate_search(index_name="security")
for i in res:
    texts.append(i['_source']['text'])

tfidf_vector = tfidf.fit_transform(texts)
print (tfidf_vector)

km=KMeans(n_clusters=4, init='k-means++',n_init=100, verbose=1)
km.fit(tfidf_vector)
print (type(tfidf_vector))
