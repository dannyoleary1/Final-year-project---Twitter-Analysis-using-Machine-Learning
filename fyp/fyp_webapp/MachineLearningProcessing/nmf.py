from __future__ import print_function
from time import time

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
import pickle
from fyp_webapp.ElasticSearch import elastic_utils
from fyp_webapp import config as cfg

def print_top_words(model, feature_names, n_top_words):
    final_res = []
    for topic_idx, topic in enumerate(model.components_):
        message = "Topic #%d: " % topic_idx
        message += " ".join([feature_names[i]
                             for i in topic.argsort()[:-n_top_words - 1:-1]])
        print(message)
        final_res.append(message)
    print()
    return final_res

def run_nmf(n_samples, n_features, n_components, n_top_words):
    texts = []
    res = elastic_utils.iterate_search(index_name=cfg.twitter_credentials['topic'])
    for i in res:
        texts.append(i['_source']['text'])


    # Use tf-idf features for NMF.
    print("Extracting tf-idf features for NMF...")
    tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2,
                                   max_features=n_features,
                                   stop_words='english')
    t0 = time()
    tfidf = tfidf_vectorizer.fit_transform(texts)
    print("done in %0.3fs." % (time() - t0))

    # Use tf (raw term count) features for LDA.
    print("Extracting tf features for LDA...")
    tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2,
                                max_features=n_features,
                                stop_words='english')
    t0 = time()
    tf = tf_vectorizer.fit_transform(texts)
    print("done in %0.3fs." % (time() - t0))
    print()

    # Fit the NMF model
    print("Fitting the NMF model (Frobenius norm) with tf-idf features, "
      "n_samples=%d and n_features=%d..."
      % (n_samples, n_features))
    t0 = time()
    nmf = NMF(n_components=n_components, random_state=1,
          alpha=.1, l1_ratio=.5).fit(tfidf)
    print("done in %0.3fs." % (time() - t0))

    print("\nTopics in NMF model (Frobenius norm):")
    tfidf_feature_names = tfidf_vectorizer.get_feature_names()
    print_top_words(nmf, tfidf_feature_names, n_top_words)

    # Fit the NMF model
    print("Fitting the NMF model (generalized Kullback-Leibler divergence) with "
      "tf-idf features, n_samples=%d and n_features=%d..."
      % (n_samples, n_features))
    t0 = time()
    nmf = NMF(n_components=n_components, random_state=1,
          beta_loss='kullback-leibler', solver='mu', max_iter=1000, alpha=.1,
          l1_ratio=.5).fit(tfidf)
    print("done in %0.3fs." % (time() - t0))

    print("\nTopics in NMF model (generalized Kullback-Leibler divergence):")
    tfidf_feature_names = tfidf_vectorizer.get_feature_names()
    print_top_words(nmf, tfidf_feature_names, n_top_words)

    tf_feature_names = tf_vectorizer.get_feature_names()
    categories = print_top_words(nmf, tf_feature_names, n_top_words)
    predict = nmf.transform(tf)
    result = {"predictions": predict, "text": texts, "categories": categories}
    return result