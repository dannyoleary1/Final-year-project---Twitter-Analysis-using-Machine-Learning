from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, render_to_response
from fyp_webapp.ElasticSearch import elastic_utils as es
from fyp_webapp import config as cfg
from fyp_webapp.TwitterProcessing import collect_tweets
import tweepy
from django.views.decorators.csrf import csrf_protect
from fyp_webapp.MachineLearningProcessing import tf_idf as tf
from fyp_webapp.MachineLearningProcessing import lda as lda
import numpy as np
from fyp_webapp import forms
from django.contrib.auth.decorators import login_required
from fyp_webapp.models import TwitterCat

@login_required(login_url='/login/')
def tweetcollector(request, template_name='fyp/CollectTweets/index.html'):
    if (request.GET.get('collect_tweets')):

        topic = cfg.twitter_credentials['topic'].replace(" ", "")
        if es.check_index_exists(topic) is None:
            es.create_index(topic)
        entries = TwitterCat.objects.filter(user=request.user)
        topics = []
        for entry in entries:
            topics.append(entry.category_name)
        stream = collect_tweets.create_stream(topics)
    if (request.GET.get('disconnect_tweets')):
        stream.disconnect()

    return render(request, template_name, {"nbar":"collect"})

@login_required
def latesttweets(request):
    topic = cfg.twitter_credentials['topic'].replace(" ", "")
    res = es.last_n_in_index(topic, number=10)
    res = res['hits']['hits']
    resultList = []
    for result in res:
        resultList.append(result['_source']['text'])
    return render_to_response('fyp/CollectTweets/latesttweets.html', {'res':resultList}, {'nbar':'collect'})