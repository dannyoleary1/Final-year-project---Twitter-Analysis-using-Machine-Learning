from django.shortcuts import get_object_or_404, render, render_to_response
from fyp_webapp.MachineLearningProcessing import tf_idf as tf
from fyp_webapp.MachineLearningProcessing import lda as lda
import numpy as np
from fyp_webapp import forms


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
                info = [()]
                for label, entry in zip(result['predictions'], result['text']):
                    info.append((np.argmax(label), entry))
            return render(request, 'fyp/TrainModel/index.html', {'LDAForm':lda_form, 'KMeansForm':kmeans_form,
                                                                 'nbar':'trainmodel', 'info': info})
    else:
        lda_form = forms.LDAForm()
        kmeans_form = forms.KMeansForm()
    return render(request, 'fyp/TrainModel/index.html', {'LDAForm':lda_form, 'KMeansForm':kmeans_form}, {'nbar':'trainmodel'} )

