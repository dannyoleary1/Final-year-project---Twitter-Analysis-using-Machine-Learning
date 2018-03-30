from celery import shared_task,current_task
from numpy import random
from scipy.fftpack import fft
from fyp_webapp.models import TwitterCat
from fyp_webapp.TwitterProcessing import preprocessor
from fyp_webapp.ElasticSearch import elastic_utils
import json
from fyp_webapp import config as cfg
from datetime import datetime, timedelta
from fyp_webapp.views.oldtweets import oldtweets
import statistics
from datetime import datetime
from collections import Counter
import tweepy

@shared_task(name="fyp_webapp.tasks.wordcloud", queue='priority_high', track_started=True)
def word_cloud(id, topic):
    item = {}
    category = []
    cat = TwitterCat.objects.filter(user_id=id)
    for entry in cat:
        entry = preprocessor.preprocess(entry.category_name)
        entry = preprocessor.porter_stemming(entry)
        entry = ''.join(c for c in entry if c not in '[]\'')
        res = (elastic_utils.search_index(topic,
                                          query='{"query":{"query_string":{"fields":["text"],"query":"%s*"}}}' % str(
                                              entry)))
        total = res['hits']['total']
        item[entry] = total
        category.append(entry)
        current_task.update_state(state='PROGRESS',
                                  meta={'current_categories': category, 'current_results': item})
    jsonData = json.dumps(item)
    return (category, jsonData)

@shared_task(name="fyp_webapp.tasks.aggregate_words")
def aggregate_words(user_id,status):
    cat = TwitterCat.objects.filter(user_id=user_id)
    assigned_cat = False
    for entry in cat:
        if str(entry.category_name) in (status['text'].lower() or status['name'].lower()):
            print (status['created'])
            topic = entry.category_name + "-latest"
            elastic_utils.create_index(topic)
            assigned_cat=True
            break
    if assigned_cat == False:
        topic = "unknown-latest"
        elastic_utils.create_index(topic)
    id = elastic_utils.last_id(topic)
    id+=1
    elastic_utils.add_entry(topic, id, status)

@shared_task(name="fyp_webapp.tasks.collect_old_tweets", queue='old_tweets')
def collect_old_tweets(topic, number_of_days):
    todays_date = datetime.now().date()
    start_date = todays_date - timedelta(days=number_of_days)
    while start_date != todays_date:
        print ("------------------------------------------")
        print ("Entry:  " + topic)
        print ("Currently on date:  " + str(start_date))
        print ("------------------------------------------")
 #   auth = tweepy.OAuthHandler(cfg.twitter_credentials["consumer_key"], cfg.twitter_credentials['consumer_secret'])
 #   auth.set_access_token(cfg.twitter_credentials['access_token'], cfg.twitter_credentials['access_token_secret'])
 #   api = tweepy.API(auth, wait_on_rate_limit=True)
 #   for status in tweepy.Cursor(api.search, q=topic, since="2018-03-22", until="2018-03-28", lang="en").items():
 #       if hasattr(status, 'retweeted_status'):
 #           continue #this filters out retweets
 #       else:
 #           try:
 #               text = status.extended_tweet["full_text"]
 #           except AttributeError:
 #               text = status.text
 #       print (status.created_at)
        tweets = oldtweets.collect_tweets(topic, start_date, (start_date + timedelta(days=1)))
        oldtweets.aggregate(tweets, topic, start_date)
        start_date += timedelta(days=1)
    return

@shared_task(name="fyp_webapp.tasks.check_index", queue='misc')
def check_index():
   print ("")



@shared_task(name="fyp_webapp.tasks.clean_indexes", queue='misc')
def clean_indexes():
    index = elastic_utils.list_all_indexes()
    for entry in index:
        count_word_frequency = Counter()
        word_counter = Counter()
        hour_break_dict = {}
        if ("-latest") not in entry:
            if ("median") not in entry:
                # we frst need to collect all todays tweets
                entry_total = elastic_utils.last_id(entry)
                if elastic_utils.check_index_exists(entry + "-latest") is True:
                    total = elastic_utils.last_id(entry + "-latest")
                    day_res = elastic_utils.iterate_search(entry + "-latest", query={
                        "query":
                            {
                                "match_all": {}
                            },
                        "sort": [
                            {
                                "last_time": {
                                    "order": "desc"
                                }
                            }
                        ]
                    })
                    for test in day_res:
                        time_of_tweet = test["_source"]["created"]
                        datetime_object = datetime.strptime(time_of_tweet, '%Y-%m-%d %H:%M:%S')
                        dateobj = datetime_object.strftime("%Y-%m-%d" )
                        count_word_frequency.update(str(datetime_object.hour))
                        if str(datetime_object.hour) in hour_break_dict:
                            hour_break_dict[str(datetime_object.hour)] += 1
                        else:
                            hour_break_dict[str(datetime_object.hour)] = 1

                        words = preprocessor.filter_multiple(str(test["_source"]["text"]), ats=True, hashtags=True,
                                                             stopwords=True, stemming=False, urls=True,
                                                             singles=True)
                        terms_all = [term for term in words]
                        word_counter.update(terms_all)
                        freq_obj = {"hour_breakdown": hour_break_dict,
                                    "word_frequency": json.dumps(word_counter.most_common(75)), "total": total,
                                    "date": dateobj, "last_time": time_of_tweet}
                    print(freq_obj)
                    elastic_utils.add_entry(entry, entry_total + 1, freq_obj)
                    elastic_utils.delete_index(entry + "-latest")
                    try:
                        elastic_utils.create_index(entry + "-latest")
                    except:
                        continue

                res = elastic_utils.iterate_search(entry)
                hour_breakdown = []
                day_breakdown = []
                minute_breakdown = []
                for result in res:
                    try:
                        if (result["_source"]["last_time"] != "No Tweets"):
                            hours = result["_source"]["hour_breakdown"]
                            if len(hours) is 24:
                                day_breakdown.append(result["_source"]["total"])
                            else:
                                day_b = ((result["_source"]["total"]/len(hours))*24)
                                day_breakdown.append(day_b)
                            day_breakdown.append(result["_source"]["total"])
                            todays_hours = []

                            print (len(hours))
                            for test in hours:
                                todays_hours.append(hours[test])
                            todays_hours.sort()
                            hour_med = statistics.median(todays_hours)
                            minute_estimate = hour_med / 60
                            hour_breakdown.append(hour_med)
                            minute_breakdown.append(minute_estimate)
                    except:
                        continue
                day_breakdown.sort()
                minute_breakdown.sort()
                hour_breakdown.sort()
                five_min_median = 0
                if (len(day_breakdown) != 0):
                    day_median = statistics.median(day_breakdown)
                else:
                    day_median = 0
                if (len(minute_breakdown) != 0):
                    minute_median = statistics.median(minute_breakdown)
                    five_min_median = minute_median*5
                else:
                    minute_median = 0
                if (len(hour_breakdown) != 0):
                    hour_median = statistics.median(hour_breakdown)
                else:
                    hour_median = 0
                es_obj = {"index": entry, "day_median": day_median, "minute_median": minute_median,
                          "hour_median": hour_median, "five_minute_median": five_min_median}
                elastic_utils.add_entry_median(entry + "-median", es_obj)


@shared_task(name="fyp_webapp.tasks.elastic_info", queue="priority_high")
def elastic_info():
    index = elastic_utils.list_all_indexes()
    index_list = []
    for entry in index:
        index_list.append(entry)
    index_list.sort()
    index_dict = {}
    current_entry = 1
    for entry in index_list:
        current_task.update_state(state='PROGRESS',
                                  meta={'entry': entry, 'current_results': index_dict, 'current_entry': current_entry, 'last_entry': len(index_list)})
        latest_entry_number = elastic_utils.last_id(entry)
        print (entry)
        print (latest_entry_number)
        if latest_entry_number != 0:
            latest_tweets = elastic_utils.last_n_in_index(entry, 5)
        index_dict[entry] = {"total": latest_entry_number, "last_entries": latest_tweets, 'current_entry': current_entry, 'last_entry': len(index_list),
                             }
        current_entry += 1
    return index_dict
