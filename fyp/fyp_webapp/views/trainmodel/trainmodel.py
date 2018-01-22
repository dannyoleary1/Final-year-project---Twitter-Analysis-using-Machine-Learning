from django.shortcuts import get_object_or_404, render, render_to_response
from fyp_webapp.MachineLearningProcessing import tf_idf as tf
from fyp_webapp.MachineLearningProcessing import lda as lda
from fyp_webapp.MachineLearningProcessing import nmf as nmf
import numpy as np
from fyp_webapp import forms
import nltk
import string
from nltk.corpus import stopwords
from collections import Counter
from fyp_webapp.TwitterProcessing import preprocessor
from fyp_webapp.examples import testlda, word2vec
from fyp_webapp.ElasticSearch import elastic_utils
from fyp_webapp import config as cfg
from fyp_webapp.TwitterProcessing import preprocessor
from sklearn.base import BaseEstimator, TransformerMixin

def trainmodel(request):

    if request.method == 'POST':
        if 'kmeans-form' in request.POST:
           return render_kmeans(request)
        elif 'lda-form' in request.POST:
            return render_lda(request)
        elif 'nmf-form' in request.POST:
           return render_nmf(request)
    else:
        lda_form = forms.LDAForm()
        kmeans_form = forms.KMeansForm()
        nmf_form = forms.NMFForm()
    return render(request, 'fyp/TrainModel/index.html', {'LDAForm':lda_form, 'KMeansForm':kmeans_form, 'NMFForm':nmf_form}, {'nbar':'trainmodel'} )

def count_words(number_word_frequency_results, list_in_question):
    nltk.download('stopwords')

    punctuation = list(string.punctuation)
    stop = stopwords.words('english') + punctuation + ['rt', 'via', '…', 'I', '’', 'The', '!']
    count_word_frequency = Counter()
    for entry in list_in_question:
        terms_all = [term for term in preprocessor.preprocess(entry) if term not in stop]
        count_word_frequency.update(terms_all)
    return count_word_frequency.most_common(number_word_frequency_results)

def render_kmeans(request):
    kmeans_form = forms.KMeansForm(request.POST)  # TODO add stuff
    lda_form = forms.LDAForm()
    nmf_form = forms.NMFForm()
    # Check if the form is valid:
    if kmeans_form.is_valid():
        clusters = kmeans_form.cleaned_data['clusters']
        n_init = kmeans_form.cleaned_data['n_init']
        verbose = kmeans_form.cleaned_data['verbose']
        result = tf.run_tf_idf(clusters, n_init, verbose)
        info = [()]
        for label, entry in zip(result['model'].labels_, result['texts']):
            info.append(label, entry)
        return render(request, 'fyp/TrainModel/index.html',
                      {'LDAForm': lda_form, 'KMeansForm': kmeans_form, 'NMFForm': nmf_form, 'nbar': 'trainmodel',
                       'info': info})

def render_lda(request):
    kmeans_form = forms.KMeansForm()
    lda_form = forms.LDAForm(request.POST)
    nmf_form = forms.NMFForm()
    # Check if the form is valid:
    if lda_form.is_valid():
        sample = lda_form.cleaned_data['samples']
        features = lda_form.cleaned_data['features']
        components = lda_form.cleaned_data['components']
        top_words = lda_form.cleaned_data['top_words']
        result = lda.run_lda(sample, features, components, top_words)
        list = []
        for entry in result['predictions']:
            if np.argmax(entry) not in list:
                list.append(np.argmax(entry))
        list.sort()
        # Dynamic solution
        result_list = []
        for entry in list:
            result_list.append([])
        for label, entry in zip(result['predictions'], result['text']):
            result_list[np.argmax(label)].append(entry)
        stats = []
        for entry in list:
            stats.append(count_words(10, result_list[entry]))

    return render(request, 'fyp/TrainModel/index.html',
                  {'LDAForm': lda_form, 'KMeansForm': kmeans_form, 'NMFForm': nmf_form,
                   'nbar': 'trainmodel', 'ldaresultlist':result_list, 'ldastats':stats,
                   'categories': result['categories']})

def render_nmf(request):
    kmeans_form = forms.KMeansForm()
    lda_form = forms.LDAForm()
    nmf_form = forms.NMFForm(request.POST)
    if nmf_form.is_valid():
        sample = nmf_form.cleaned_data['samples']
        features = nmf_form.cleaned_data['features']
        components = nmf_form.cleaned_data['components']
        top_words = nmf_form.cleaned_data['top_words']
        result = nmf.run_nmf(sample, features, components, top_words)
        list = []
        for entry in result['predictions']:
            if np.argmax(entry) not in list:
                list.append(np.argmax(entry))
        list.sort()
        #Dynamic solution
        result_list = []
        for entry in list:
            result_list.append([])
        for label,entry in zip(result['predictions'], result['text']):
            result_list[np.argmax(label)].append(entry)
        stats = []
        for entry in list:
            stats.append(count_words(10, result_list[entry]))
        test()
    return render(request, 'fyp/TrainModel/index.html',
                  {'LDAForm': lda_form, 'KMeansForm': kmeans_form, 'NMFForm': nmf_form, 'nbar': 'trainmodel', 'nmfresultlist':result_list,
                   'nmfcategories': result['categories'], 'nmfstats':stats})

def test():
    texts = []
    res = elastic_utils.iterate_search(index_name=cfg.twitter_credentials['topic'])
    for i in res:
        processed_text = preprocessor.preprocess(i['_source']['text'])
        processed_text = preprocessor.remove_stop_words(processed_text) #remove stop words
        processed_text = preprocessor.remove_urls(processed_text) #remove urls
        processed_text = preprocessor.remove_ats(processed_text) #remove username requests
        processed_text = preprocessor.remove_hashtags(processed_text) #remove hashtags? #TODO this might be useful
        texts.append(processed_text)
    doc_2_vec = testlda.run(texts)

    #print (doc_2_vec.fit(texts))
