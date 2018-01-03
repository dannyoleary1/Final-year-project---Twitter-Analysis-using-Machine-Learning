from django.shortcuts import get_object_or_404, render, render_to_response
from fyp_webapp.MachineLearningProcessing import tf_idf as tf
from fyp_webapp.MachineLearningProcessing import lda as lda
import numpy as np
from fyp_webapp import forms
import nltk
import string
from nltk.corpus import stopwords
from collections import Counter
from fyp_webapp.TwitterProcessing import preprocessor

def trainmodel(request):

    if request.method == 'POST':
        if 'kmeans-form' in request.POST:
            #Do Stuff
            kmeans_form = forms.KMeansForm(request.POST) #TODO add stuff
            lda_form = forms.LDAForm()
            # Check if the form is valid:
            if kmeans_form.is_valid():
                clusters = kmeans_form.cleaned_data['clusters']
                n_init = kmeans_form.cleaned_data['n_init']
                verbose = kmeans_form.cleaned_data['verbose']
                result = tf.run_tf_idf(clusters, n_init, verbose)
                info = [()]
                for label, entry in zip(result['model'].labels_, result['texts']):
                    info.append(label, entry)
                return render(request, 'fyp/TrainModel/index.html', {'LDAForm':lda_form, 'KMeansForm':kmeans_form, 'nbar':'trainmodel',
                                                                     'info':info})
        elif 'lda-form' in request.POST:
            kmeans_form = forms.KMeansForm()
            lda_form = forms.LDAForm(request.POST)

            # Check if the form is valid:
            if lda_form.is_valid():
                sample = lda_form.cleaned_data['samples']
                features = lda_form.cleaned_data['features']
                components = lda_form.cleaned_data['components']
                top_words = lda_form.cleaned_data['top_words']
                result = lda.run_lda(sample, features, components, top_words)
                list1 = []
                list2 = []
                list3 = [] #TODO THIS MAY NEED TO BE A MORE DYNAMIC APPROACH
                info = [()]
                for label, entry in zip(result['predictions'], result['text']):
                    if(np.argmax(label) == 0):
                        list1.append(entry)
                    elif(np.argmax(label) == 1):
                        list2.append(entry)
                    else:
                        list3.append(entry)
            list1_word_count = count_words(10, list1)
            list2_word_count = count_words(10, list2)
            list3_word_count = count_words(10, list3)
            return render(request, 'fyp/TrainModel/index.html', {'LDAForm':lda_form, 'KMeansForm':kmeans_form,
                                                                 'nbar':'trainmodel', 'list1': list1, 'list2':list2,'list3':list3,
                                                                 'list1wordcount': list1_word_count, 'list2wordcount': list2_word_count,
                                                                 'list3wordcount': list3_word_count,
                                                                 'categories':result['categories']})
    else:
        lda_form = forms.LDAForm()
        kmeans_form = forms.KMeansForm()
    return render(request, 'fyp/TrainModel/index.html', {'LDAForm':lda_form, 'KMeansForm':kmeans_form}, {'nbar':'trainmodel'} )

def count_words(number_word_frequency_results, list_in_question):
    nltk.download('stopwords')

    punctuation = list(string.punctuation)
    stop = stopwords.words('english') + punctuation + ['rt', 'via', '…', 'I', '’', 'The', '!']
    count_word_frequency = Counter()
    for entry in list_in_question:
        terms_all = [term for term in preprocessor.preprocess(entry) if term not in stop]
        count_word_frequency.update(terms_all)
    return count_word_frequency.most_common(number_word_frequency_results)