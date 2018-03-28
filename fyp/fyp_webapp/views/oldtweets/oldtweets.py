from django.shortcuts import get_object_or_404, render, render_to_response, HttpResponseRedirect
from fyp_webapp.ElasticSearch import elastic_utils
from django.contrib.auth.decorators import login_required
from fyp_webapp import forms
import datetime
from fyp_webapp.TwitterProcessing import preprocessor
from fyp_webapp.TwitterProcessing import termsfrequency
from fyp_webapp.TwitterProcessing import collect_old_tweets
import string
from fyp_webapp.TwitterProcessing import preprocessor
import nltk
from nltk.corpus import stopwords
from collections import Counter
import json

@login_required(login_url="/login/")
def oldtweets(request):
    if request.POST:
        completed_form = forms.OldTweetsForm(request.POST)
        if completed_form.is_valid():
            cleaned = completed_form.clean()
            index_name = cleaned['index_name']
            search_query = cleaned['query_search']
            start_date = cleaned['start_date']
            end_date = cleaned['end_date'] + datetime.timedelta(days=1)
            end_tweets = []
            if elastic_utils.check_index_exists(index_name) is None:
                elastic_utils.create_index(index_name)
            while start_date != end_date:
                tweets = collect_tweets(search_query, start_date, (start_date+datetime.timedelta(days=1)))
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
    common_words = []
    for entry in tweet:
        if entry.date.hour == current_hour:
            current_tweet_count += 1
        else:
            data[current_hour] = current_tweet_count
            current_hour = current_hour - 1
            current_tweet_count = 1
        common_words.append(
                preprocessor.filter_multiple(str(entry.text), ats=True, stopwords=True, stemming=False, urls=True, singles=True))
    #TODO if no entries in tweet it won't work properly since it skips the for loop. Captured only for hour 23 in that case.
    count_word_frequency = Counter()
    for entry in common_words:
        terms_all = [term for term in entry]
        count_word_frequency.update(terms_all)
    data[current_hour] = current_tweet_count
    words = count_word_frequency.most_common(50)
    try:
        dict = {"date": str(start_date), "total": len(tweet), "last_time": tweet[len(tweet) - 1].date, "hour_breakdown": data, 'words': json.dumps(words)}
    except:
        dict = {"date": str(start_date), "total": len(tweet), "last_time": "No Tweets",
                "hour_breakdown": data, 'words': json.dumps(words)}
    id = elastic_utils.last_id(topic)
    id += 1
    elastic_utils.add_entry(topic, id, dict)