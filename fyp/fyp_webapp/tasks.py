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
    todays_date = datetime.today()
    start_date = todays_date - timedelta(days=number_of_days)
    while start_date != todays_date:
        print ("Currently on date:  " + str(start_date))
        tweets = oldtweets.collect_tweets(topic, start_date, (start_date + timedelta(days=1)))
        oldtweets.aggregate(tweets, topic, start_date)
        start_date += timedelta(days=1)
    return

@shared_task(name="fyp_webapp.tasks.check_index", queue='misc')
def check_index():
    #assign the median value.
    print ("")


@shared_task(name="fyp_webapp.tasks.clean_indexes", queue='misc')
def clean_indexes():
    index = elastic_utils.list_all_indexes()
    for entry in index:
        count_word_frequency = Counter()
        word_counter = Counter()
        if ("-latest") not in entry:
            if ("median") not in entry:
                res = elastic_utils.iterate_search(entry)
                hour_breakdown = []
                day_breakdown = []
                minute_breakdown = []
                for result in res:
                    try:
                        if (result["_source"]["last_time"] != "No Tweets"):
                            day_breakdown.append(result["_source"]["total"])
                            todays_hours = []
                            hours = result["_source"]["hour_breakdown"]
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
                if (len(day_breakdown) != 0):
                    day_median = statistics.median(day_breakdown)
                else:
                    day_median = 0
                if (len(minute_breakdown) != 0):
                    minute_median = statistics.median(minute_breakdown)
                else:
                    minute_median = 0
                if (len(hour_breakdown) != 0):
                    hour_median = statistics.median(hour_breakdown)
                else:
                    hour_median = 0
                es_obj = {"index": entry, "day_median": day_median, "minute_median": minute_median,
                          "hour_median": hour_median}
                elastic_utils.add_entry_median(entry + "-median", es_obj)
        else:
            res = elastic_utils.iterate_search(entry)
            total = elastic_utils.last_id(entry)
            for result in res:
                try:
                    created = result["_source"]["created"]
                    datetime_object = datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
                    count_word_frequency.update(str(datetime_object.hour))
                    words = preprocessor.filter_multiple(str(result["_source"]["created"]), ats=True, stopwords=True, stemming=False, urls=True,
                                                 singles=True)
                    terms_all = [term for term in words]
                    word_counter.update(terms_all)
                    freq_obj = {"hour_breakdown": count_word_frequency.most_common(24), "word_frequency": word_counter.most_common(75), "total": total, "date": (str(datetime.today() - timedelta(days=1)))}
                    print(freq_obj)
                except:
                    continue
    for entry in index:
        if ("-latest") in index:
            elastic_utils.delete_index(entry)

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
        if latest_entry_number != 0:
            latest_tweets = elastic_utils.last_n_in_index(entry, 5)
        index_dict[entry] = {"total": latest_entry_number, "last_entries": latest_tweets, 'current_entry': current_entry, 'last_entry': len(index_list),
                             }
        current_entry += 1
    return index_dict
