from django.shortcuts import get_object_or_404, render, render_to_response, HttpResponseRedirect
from fyp_webapp.ElasticSearch import elastic_utils
from django.contrib.auth.decorators import login_required
from fyp_webapp import forms
import datetime
from fyp_webapp.TwitterProcessing import preprocessor
from fyp_webapp.TwitterProcessing import termsfrequency
from fyp_webapp.TwitterProcessing import collect_old_tweets
import string
import nltk
from nltk.corpus import stopwords
from collections import Counter

@login_required(login_url="/login/")
def oldtweets(request):
    if request.POST:
        print ("got post request")
        completed_form = forms.OldTweetsForm(request.POST)
        if completed_form.is_valid():
            cleaned = completed_form.clean()
            index_name = cleaned['index_name']
            start_date = cleaned['start_date']
            end_date = cleaned['end_date'] + datetime.timedelta(days=1)
            end_tweets = []
            if elastic_utils.check_index_exists(index_name) is None:
                elastic_utils.create_index(index_name)
                tweets = collect_tweets(index_name, start_date, (start_date+datetime.timedelta(days=1)))
                aggregate(tweets, index_name, start_date)
                start_date += datetime.timedelta(days=1)

    es_index_form = forms.OldTweetsForm()
    return render(request, "fyp/oldtweets/index.html", {"oldtweetsform": es_index_form})

def collect_tweets(index, start, end):
    tweet = collect_old_tweets.run(query_search=index, start_date=str(start), end_date=str(end))
    return tweet

def aggregate(tweet, topic, start_date):
    data = {}
    current_hour = 23
    current_tweet_count = 0
    for entry in tweet:
        if entry.date.hour == current_hour:
            current_tweet_count += 1
        else:
            data[current_hour] = current_tweet_count
            current_hour = current_hour - 1
            current_tweet_count = 1

    data[current_hour] = current_tweet_count

    dict = {"date": str(start_date), "total": len(tweet), "last_time": tweet[len(tweet) - 1].date, "hour_breakdown": data}
    id = elastic_utils.last_id(topic)
    id += 1
    elastic_utils.add_entry(topic, id, dict)
    print(id)