from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from fyp_webapp.ElasticSearch import elastic_utils as es
from fyp_webapp import config as cfg
from fyp_webapp.TwitterProcessing import collect_tweets
import tweepy

def fyp(request):
    return HttpResponse("Hello, world. You're at the index.")

def tweetcollector(request):

    if (request.GET.get('collect_tweets')):
       stream = collect_tweets.create_stream()

    return render(request, 'fyp/CollectTweets/index.html')