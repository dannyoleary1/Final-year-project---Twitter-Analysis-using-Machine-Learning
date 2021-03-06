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
import time
from channels import Group
import json
from channels import Channel
from channels.auth import channel_session_user
from fyp_webapp import tasks
from fyp_webapp import models
import ast

@shared_task(name="fyp_webapp.tasks.wordcloud", queue='priority_high', track_started=True)
def word_cloud(id, topic):
    """The word cloud task creates a word cloud from the data."""
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
    """The aggregate_words task adds Tweets to Elasticsearch live from the Celery Queue."""
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
    """Collect Old Tweets task will run the old_tweets function to collect a series of old tweets for a new topic."""
    todays_date = datetime.now().date()
    start_date = todays_date - timedelta(days=number_of_days)
    while start_date != todays_date:
        print ("------------------------------------------")
        print ("Entry:  " + topic)
        print ("Currently on date:  " + str(start_date))
        print ("------------------------------------------")
        tweets = oldtweets.collect_tweets(topic, start_date, (start_date + timedelta(days=1)))
        oldtweets.aggregate(tweets, topic, start_date)
        start_date += timedelta(days=1)
    return

@shared_task(name="fyp_webapp.tasks.check_index", queue='misc')
def check_index():
    """Check index is the main algorithm. It will detect trends in real time. This task runs every 5 minutes."""
    index = elastic_utils.list_all_indexes()
    ts = datetime.now() - timedelta(minutes=5)
    total_count = 0
    for entry in index:
        word_counter = Counter()
        if ("-latest") not in entry:
            if ("median") not in entry:
                if elastic_utils.check_index_exists(entry + "-latest") is True:
                    total = elastic_utils.last_id(entry + "-latest")
               #     t = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                    day_res = elastic_utils.iterate_search(entry + "-latest", query={
                        "query":
                            {
                                "match_all": {}
                            },
                        "sort": [
                            {
                                "created.keyword": {
                                    "order": "desc"
                                }
                            }
                        ]
                    })
                    total_in_five = 0
                    tweet_list = []
                    name = []
                    for item in day_res:
                            time_of_tweet = item["_source"]["created"]
                            datetime_object = datetime.strptime(time_of_tweet, '%Y-%m-%d %H:%M:%S')
                            if datetime_object > ts:
                                if name.count(item["_source"]["name"]) < 3:
                                    print ("in here")
                                    print (name)
                                    name.append(item["_source"]["name"])
                                    tweet_list.append(str(item["_source"]["text"]))
                                    total_in_five += 1
                                    words = preprocessor.filter_multiple(str(item["_source"]["text"]), ats=True, hashtags=True,
                                                                 stopwords=True, stemming=False, urls=True,
                                                                 singles=True)
                                    terms_all = [term for term in words]
                                    terms_all = set(terms_all)
                                    word_counter.update(terms_all)
                                else:
                                    break #stop iterating through every entry. This will save a lot of time.
                    res = elastic_utils.iterate_search(entry+"-median")
                    potential_keywords = []
                    for median in res:
                        breakdown = median["_source"]["five_minute_median"]
                        if (total_in_five is 0):
                            total_five_ratio = 0
                        elif (breakdown is 0):
                            total_five_ratio = 0
                        elif (breakdown < 1):
                            total_five_ratio = 1
                        else: total_five_ratio = total_in_five/breakdown
                        if (total_five_ratio > 2.0):
                            potential_keywords.append((entry,total_five_ratio,entry,"Monthly"))
                    yesterdays_res = median["_source"]["yesterday_res"]

                    for key, value in word_counter.items():
                        current_word = word_counter[key]
                        if (current_word > 5):
                            if key in yesterdays_res:
                                test_var = ((yesterdays_res[key][0]/24)/60)*5
                                current_word_ratio = current_word/test_var
                                if key == entry:
                                    if (current_word_ratio > 2.5):
                                        potential_keywords.append((entry,current_word_ratio,key,"Yesterday"))
                                        continue
                                elif (current_word_ratio > 2.0):
                                    potential_keywords.append((entry,current_word_ratio,key,"Yesterday"))
                        existing_words = median["_source"]["day_words_median"]
                        existing_dev = median["_source"]["standard_dev"]


                        if (current_word > 5):
                            if key in existing_words:
                                existing_val = existing_words[key]
                                existing_val = ((existing_val/24)/60)*5
                                standard_dev_5_mins = ((existing_dev[key]/24)/60)*5
                                compared_to_monthly_ratio = current_word/existing_val
                                if (current_word>(standard_dev_5_mins+existing_val+standard_dev_5_mins)):
                                    potential_keywords.append((entry,(current_word-(standard_dev_5_mins+existing_val+standard_dev_5_mins)),key,"Deviation"))
                                if (compared_to_monthly_ratio > 1.9):
                                    potential_keywords.append((entry, compared_to_monthly_ratio, key, "Monthly"))
                        if (current_word > 6 and key not in existing_words and key not in yesterdays_res):
                            potential_keywords.append((entry, current_word, key, "No Entries"))
                    notification = check_percentage(entry, tweet_list, potential_keywords)

                    if "total" in  notification:
                        print ("--------")
                        print (notification)
                        print (notification["total"])
                        total_count += notification["total"]
    data = json.dumps({'job': total_count})
    Group('notifications').send({'text': data})


def check_percentage(topic, tweet_list, potential_keywords):
    """Checks if the current entry breaks the threshold."""
    #We need to try see if they relate to each other.
    #How many times do the words appear with each other.
    lets_test = []
    datetime_object = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    combined_words_set = set()
    total = 0
    json_obj = {}
    for entry in potential_keywords:
        for test in potential_keywords:
            if entry == test:
                continue
            #check tweet_list
            entries_combined_total = 0
            single = 0
            for tweet in tweet_list:
                if str(test[2]).lower() in tweet.lower() and str(entry[2]).lower() in tweet.lower():
                    entries_combined_total += 1
                    single += 1
                elif (str(entry[2]).lower() in tweet.lower()):
                    single += 1
            percentage = ((entries_combined_total/single)*100)
            if percentage > 0:
                #temp_set = set([entry[2], test[2]])
                combined_words_set.add(entry[2])
                combined_words_set.add(test[2])
    if len(combined_words_set) != 0:
        lets_test.append((topic, combined_words_set))
        cat = models.NotificationTracked.objects.filter(topic=topic)
        #models.NotificationTracked.objects.all().delete()
        if len(cat) is 0 and len(combined_words_set) is not 0:
            keywords = json.dumps(list(combined_words_set))
            new_notification = models.NotificationTracked(topic=topic, keywords=keywords, date=datetime_object)
            total+=1
            if len(models.NotificationTracked.objects.filter(keywords=keywords))>0:
                new_notification.save()
        else:
            for mod in cat:
                uh = json.dumps(mod.keywords)
                jsonDec = json.decoder.JSONDecoder()
                myPythonList = jsonDec.decode(uh)
                x = ast.literal_eval(myPythonList)
                print (x)
                print (combined_words_set)
                test = set.intersection(set(x), combined_words_set)
                percentage = (len(test)/len(combined_words_set)*100)
                if percentage > 60:
                    temp = set(x).union(combined_words_set)
                    keywords = json.dumps(list(temp))
                    total += 1
                    mod.keywords = keywords
                    if len(models.NotificationTracked.objects.filter(keywords=keywords)) > 0:
                        mod.save()
                else:
                    keywords = json.dumps(list(combined_words_set))
                    new_mod = models.NotificationTracked(topic=topic, keywords=keywords, date=datetime_object)
                    total+=1
                    print (keywords)
                    if len(models.NotificationTracked.objects.filter(keywords=keywords)) > 0:
                        new_mod.save()
        json_obj = {"topic": topic, "keywords":keywords, "total":total}

    return json_obj

def collect_todays_tweets(entry):
    """Collects todays tweets for every topic."""
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
                    dateobj = datetime_object.strftime("%Y-%m-%d")
                    created_at = datetime_object.strftime("%Y-%m-%dT%H:%M:%S")
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
                                "words": json.dumps(word_counter.most_common(400)), "total": total,
                                "date": dateobj, "last_time": created_at}
                    elastic_utils.add_entry(entry, entry_total + 1, freq_obj)
                    elastic_utils.delete_index(entry + "-latest")
                try:
                    elastic_utils.create_index(entry + "-latest")
                except:
                    print ("Todays index already exists! This is an exception, but it's probably ok")


def get_median(entry):
        """Calculates the median for every topic."""
        # Now get yesterdays entries
        #I need to keep track of the value for words over each day, and also need day/hour breakdowns for each entry.
        day_breakdown = []
        hour_breakdown = []
        minute_breakdown = []
        latest_words = {}

        day_res = elastic_utils.iterate_search(entry, query={
            "query":
                {
                    "match_all": {}
                },
            "sort": [
                {
                    "date": {
                        "order": "desc"
                    }
                }
            ]
        })

        ##iterate through entries by date.
        day = 0
        yesterday_res = {}
        for latest in day_res:
            try:
                hours = latest["_source"]["hour_breakdown"]
            except:
                hours = "No Tweets"
                continue
            #This is a words setup.
            if (hours != "No Tweets"):
                latest_ent = json.dumps(latest['_source']['words'])
                latest_ent = latest_ent.replace("\"[", "")
                latest_ent = latest_ent.replace("]\"", "")
                latest_ent = (latest_ent.split("], ["))

                for data in latest_ent:
                    data = data.replace("[", "")
                    data = data.replace("\"", "")
                    data = data.replace("\\", "")
                    data = data.replace("[\'", "")
                    data = data.replace("\']", "")
                    data = data.replace("]", "")
                    terms_all = [data.split(", ")[0]]
                    print (entry)
                    total = [data.split(", ")[1]]
                    if len(hours) <24:
                        total[0] = (int(total[0])/int(len(hours)))*24
                    if terms_all[0] in latest_words:
                        if "." in terms_all[0]:
                            terms_all[0] = terms_all[0].replace(".", "dot")
                        elif "," in terms_all[0]:
                            terms_all[0] = terms_all[0].replace(",", "comma")
                        latest_words[terms_all[0]].append(int(total[0]))
                    else:
                        if "." in terms_all[0]:
                            terms_all[0] = terms_all[0].replace(".", "dot")
                        elif "," in terms_all[0]:
                            terms_all[0] = terms_all[0].replace(",", "comma")
                        latest_words[terms_all[0]] = []
                        latest_words[terms_all[0]].append(int(total[0]))
                    if day is 0:
                        if terms_all[0] in yesterday_res:
                            if "." in terms_all[0]:
                                terms_all[0] = terms_all[0].replace(".", "dot")
                            elif "," in terms_all[0]:
                                terms_all[0] = terms_all[0].replace(",", "comma")
                            yesterday_res[terms_all[0]].append(int(total[0]))
                        else:
                            if "." in terms_all[0]:
                                terms_all[0] = terms_all[0].replace(".", "dot")
                            elif "," in terms_all[0]:
                                terms_all[0] = terms_all[0].replace(",", "comma")
                            yesterday_res[terms_all[0]] = []
                            yesterday_res[terms_all[0]].append(int(total[0]))

            #Now dealing with the breakdown over time
                if len(hours) is 24:
                    day_breakdown.append(latest["_source"]["total"])
                else:
                    day_b = ((latest["_source"]["total"] / len(
                        hours)) * 24)  # This is to combat when all entries aren't collected.
                    day_breakdown.append(day_b)
                todays_hours = []  # A list of all the hours captured fors total..
                for test in hours:
                    todays_hours.append(hours[test])
                todays_hours.sort()
                hour_med = statistics.median(todays_hours)  # gets the median for the hours for the specific day
                minute_estimate = hour_med / 60  # divide by 60 to get a minutes median
                hour_breakdown.append(hour_med)
                minute_breakdown.append(minute_estimate)
                day +=1

        #Now to calculate setup.
        day_breakdown.sort()
        minute_breakdown.sort()
        hour_breakdown.sort()
        five_min_median = 0
        count = elastic_utils.count_entries(entry)
        totals_array = add_zeros(latest_words, count)
        standard_dev = totals_array[1]
        totals_array = totals_array[0]

        five_min_word_breakdown = {}

        if (len(day_breakdown) != 0):
            day_median = statistics.median(day_breakdown)
        else:
            day_median = 0
        if (len(minute_breakdown) != 0):
            minute_median = statistics.median(minute_breakdown)
            five_min_median = minute_median * 5
        else:
            minute_median = 0
        if (len(hour_breakdown) != 0):
            hour_median = statistics.median(hour_breakdown)
        else:
            hour_median = 0
        es_obj = {"index": entry, "day_median": day_median, "minute_median": minute_median,
              "hour_median": hour_median, "five_minute_median": five_min_median, "day_words_median": totals_array,
              "yesterday_res": yesterday_res, "standard_dev": standard_dev}
        if "-median" not in entry:
            if elastic_utils.check_index_exists(entry + "-median") == False:
                elastic_utils.create_index(entry + "-median")
        elastic_utils.add_entry_median(entry + "-median", es_obj)



@shared_task(name="fyp_webapp.tasks.clean_indexes", queue='misc')
def clean_indexes():
    """Purges the index at night."""
    print ("Started cleaning and median collection.")
    index = elastic_utils.list_all_indexes()
    for entry in index:

        if ("-latest") not in entry:
            if "-median" not in entry:
                #collect_todays_tweets(entry) #TODO commented out when testing
                get_median(entry)






@shared_task(name="fyp_webapp.tasks.elastic_info", queue="priority_high")
def elastic_info(index_list):
    """Displays statistics from the topics."""
    final_res = []
    current_entry = 0
    all_entries = []
    for entry in index_list:
        index_dict = {}
        all_entries.append(entry)
        index_dict["name"] = {}
        index_dict["current_entry"] = entry
        if current_entry is 0:
            current_task.update_state(state='PROGRESS',
                                      meta={'current_percentage': 0, "current_entry":entry})

        res = elastic_utils.search_index(entry, query={
                        "query":
                            {
                                "match_all": {}
                            },
                        "sort": [
                            {
                                "date": {
                                    "order": "desc"
                                }
                            }
                        ],
            "size":10
                    })

        current_array = []
        for current in res["hits"]["hits"]:
            test = {}
            test["date"] = current["_source"]["date"]
            test["total"] = current["_source"]["total"]
            test["last_collected"] = current["_source"]["last_time"]
            current_array.append(test)
        index_dict["name"]["current"] = current_array

        median_array = []
        res_median = elastic_utils.iterate_search(entry + "-median")
        for median in res_median:
            med = {}
            med["day_median"] = median["_source"]["day_median"]
            med["hour_median"] = median["_source"]["hour_median"]
            med["minute_median"] = median["_source"]["minute_median"]
            median_array.append(med)
        index_dict["name"]["median"] = median_array
        res_latest = elastic_utils.search_index(entry+"-latest", query={
                        "query":
                            {
                                "match_all": {}
                            },
                        "sort": [
                            {
                                "created.keyword": {
                                    "order": "desc"
                                }
                            }
                        ],
            "size":5
                    })

        latest_array = []
        for item in res_latest["hits"]["hits"]:
            cur_entry = {}
            cur_entry["created"] = item["_source"]["created"]
            cur_entry["text"] = item["_source"]["text"]
            cur_entry["image"] = item["_source"]["profile_picture"]
            cur_entry["name"] = item["_source"]["name"]
            latest_array.append(cur_entry)

        index_dict["name"]["latest"] = latest_array

        all_entries.append(latest_array)
        if current_entry is not 0:
            current_task.update_state(state='PROGRESS', meta={
                'current_percentage': (current_entry/len(index_list))*100, 'current_entry':entry, 'final_res': final_res
            })
        current_entry += 1
        final_res.append(index_dict)
    print (len(final_res))
    return final_res

@shared_task(name="fyp_webapp.tasks.test_job", queue="priority_high")
def test_job(reply_channel):
    """Test job, can probably be deleted now"""
    data = {"job": "accept"}
    Group('notifications').send({'text': data})

def add_zeros(data, count):
    """Adds zeroes to the arrays."""
#    print ("number of entries:    " + str(len(data)))
    temp_arr = {}
    dev_arr = {}
    for item in data:
        print ("--")
        print (item)
        size = len(data[item])
        if type(count) is int:
            count = count
        else:
            count = count['count']

        print ("size:    " + str(size))
        print ("count:    " + str(count))
        print ("data:    " + str(item))
        print ("data    " + str(data[item]))
        if (int(size) > int(count)/5):
            #TODO calc mean or standard deviation?
            data[item].sort()

            #Take mean away from standard deviation
            day_stdev = statistics.stdev(data[item])
            data[item] = statistics.mean(data[item])
#            print ("One standard Deviation away:    " + str(day_stdev))
            if (data[item] > 1):
                temp_arr[item] = data[item]
                dev_arr[item] = day_stdev
    return (temp_arr,dev_arr)

@shared_task(name="fyp_webapp.tasks.setup_charts", queue="priority_high")
def setup_charts(cat):
    """Sets up the data for the charts on the front end."""
    tot = len(cat)
    entries_arrays = []
    i = 0
    for mod in cat:
        current_entry = []
        current_entry.append(mod)
        res = elastic_utils.iterate_search(index_name=mod, query={
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
            ],
            "size": 20,
        })
        i+=1
        for entry in res:
            current_entry.append(entry["_source"]["total"])
        if i != (tot-1):
            current_task.update_state(state='PROGRESS',
                                      meta={'current_percentage': (i / tot) * 100, 'current_entry': mod,
                                            "chart_data": entries_arrays})
        else:
            current_task.update_state(state='PROGRESS',
                                      meta={'current_percentage': (i / tot) * 100, 'current_entry': mod,
                                            "chart_data": entries_arrays, "latest_chart_data": current_entry, "test": 'Finished'})

        entries_arrays.append(current_entry)
    print ("task finished.")
    return entries_arrays
