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




@shared_task(name="fyp_webapp.tasks.ftt_random")
def fft_random(n):
    """
    Brainless number crunching just to have a substantial task:
    """
    for i in range(n):
        x = random.normal(0, 0.1, 2000)
        y = fft(x)
        if(i%30 == 0):
            process_percent = int(100 * float(i) / float(n))
            current_task.update_state(state='PROGRESS',
                                      meta={'process_percent': process_percent})
    return random.random()

@shared_task
def add(x,y):
    for i in range(1000000000):
        a = x+y
    return x+y

@shared_task(name="fyp_webapp.tasks.wordcloud", queue='priority_high', track_started=True)
def word_cloud(id, topic):
    item = {}
    category = []
    cat = TwitterCat.objects.filter(user_id=id)
    for entry in cat:
        print("----------")
        print(entry)
        print("---------")

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
        print (entry.category_name)
        if str(entry.category_name) in (status['text'].lower() or status['name'].lower()):
            topic = entry.category_name + "-latest"
            elastic_utils.create_index(topic)
            assigned_cat=True
            break
    if assigned_cat == False:
        print ("------------------------")
        print ("Text says:  " + str(status['text']))
        print ("------------------------")
        topic = "unknown-latest"
        elastic_utils.create_index(topic)
    print (topic)
    id = elastic_utils.last_id(topic)
    id+=1
    elastic_utils.add_entry(topic, id, status)

@shared_task(name="fyp_webapp.tasks.collect_old_tweets", queue='old_tweets')
def collect_old_tweets(topic, number_of_days):
    todays_date = datetime.today()
    print (str(todays_date))
    start_date = todays_date - timedelta(days=number_of_days)
    while start_date != todays_date:
        print ("Currently on date:  " + str(start_date))
        tweets = oldtweets.collect_tweets(topic, start_date, (start_date + timedelta(days=1)))
        oldtweets.aggregate(tweets, topic, start_date)
        start_date += timedelta(days=1)
    return

@shared_task(name="fyp_webapp.tasks.check_index", queue='misc')
def check_index():
    print ("Does this run every 10 seconds?")
    #assign the median value.
    index = elastic_utils.list_all_indexes()
    index_list = []
    for entry in index:
        if "-latest" not in entry:
            res = elastic_utils.iterate_search(entry)
            hour_breakdown = []
            day_breakdown = []
            minute_breakdown = []
            for result in res:
                try:
                    if (result["_source"]["last_time"] != "No Tweets"):
                        print (result["_source"]["total"])
                        day_breakdown.append(result["_source"]["total"])
                        todays_hours = []
                        hours = result["_source"]["hour_breakdown"]
                        for test in hours:
                            todays_hours.append(hours[test])
                        todays_hours.sort()
                        hour_med = statistics.median(todays_hours)
                        minute_estimate = hour_med/60
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
            es_obj = {"index": entry, "day_median": day_median, "minute_median": minute_median, "hour_median":hour_median}
            elastic_utils.add_entry_median(entry, es_obj)


@shared_task(name="fyp_webapp.tasks.clean_indexes", queue='misc')
def clean_indexes():
    print ("runs at midnight.")

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
