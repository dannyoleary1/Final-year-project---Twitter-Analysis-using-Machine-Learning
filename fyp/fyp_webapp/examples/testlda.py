import gensim.models as g
import gensim

import logging
import time
import collections
import random
from nltk.cluster import KMeansClusterer, euclidean_distance, cosine_distance
import nltk
from sklearn.cluster import DBSCAN

def read_documents(documents, tokens_only=False):
    for i, line in enumerate(documents):
        line = " ".join(str(x) for x in line)
        if tokens_only:
            yield gensim.utils.simple_preprocess(line)
        else:
            # For training data, add tags
#            yield LabeledSentence(words=line, labels=[i])
            yield gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(line), [i])

def kmeans_test(model, documents):
    count = len(documents)
    vectors = []

    print("done")
    kclusterer = KMeansClusterer(20, distance=nltk.cluster.util.cosine_distance, repeats=25)
    assigned_clusters = kclusterer.cluster(model.docvecs, assign_clusters=True)

def dbscan_test(model, train_corpus):
    dbscan = DBSCAN(eps=0.3, min_samples=15)
    dbscan.fit(model.docvecs)
    words = []
    for doc_id in range(len(train_corpus)):
        words.append(train_corpus[doc_id].words)
    labels = dbscan.fit_predict(model.docvecs)
    res = zip(words, labels)
    counter = collections.Counter(labels)
    print(counter.most_common(100))
    # [(1, 4), (2, 4), (3, 2)]
   # for entry in res:
   #   print(entry)

def run(documents):
    res = []
    train_corpus = list(read_documents(documents))
    model = g.doc2vec.Doc2Vec(size=100, min_count=1, iter=100)
    model.build_vocab(train_corpus)
    model.train(train_corpus, total_examples=model.corpus_count, epochs=model.iter)

    ranks = []
    second_ranks = []
    for doc_id in range(len(train_corpus)):
        inferred_vector = model.infer_vector(train_corpus[doc_id].words)
        sims = model.docvecs.most_similar([inferred_vector], topn=len(model.docvecs))
        rank = [docid for docid, sim in sims].index(doc_id)
        ranks.append(rank)

        second_ranks.append(sims[1])
    print (collections.Counter(ranks))  # Results vary due to random seeding and very small corpus

    print('Document ({}): «{}»\n'.format(809, ' '.join(train_corpus[809].words)))
    print(u'SIMILAR/DISSIMILAR DOCS PER MODEL %s:\n' % model)
    for label, index in [('MOST', 0), ('MEDIAN', len(sims) // 2), ('LEAST', len(sims) - 1)]:
        print(u'%s %s: «%s»\n' % (label, sims[index], ' '.join(train_corpus[sims[index][0]].words)))

    dbscan_test(model, train_corpus)
