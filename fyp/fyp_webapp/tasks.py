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
    index = elastic_utils.list_all_indexes()
    ts = datetime.now() - timedelta(minutes=5)
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
                                "last_time": {
                                    "order": "desc"
                                }
                            }
                        ]
                    })
                    total_in_five = 0
                    tweet_list = []
                    for item in day_res:
                        time_of_tweet = item["_source"]["created"]
                        datetime_object = datetime.strptime(time_of_tweet, '%Y-%m-%d %H:%M:%S')
                        if datetime_object > ts:
                            tweet_list.append(str(item["_source"]["text"]))
                            total_in_five += 1
                            words = preprocessor.filter_multiple(str(item["_source"]["text"]), ats=True, hashtags=True,
                                                                 stopwords=True, stemming=False, urls=True,
                                                                 singles=True)
                            terms_all = [term for term in words]
                            terms_all = set(terms_all)
                            word_counter.update(terms_all)
                        else:
                            continue #stop iterating through every entry. This will save a lot of time.
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
                                    potential_keywords.append((entry,current_word,key,"Deviation"))
                                if (compared_to_monthly_ratio > 1.9):
                                    potential_keywords.append((entry, compared_to_monthly_ratio, key, "Monthly"))
                        if (current_word > 6 and key not in existing_words and key not in yesterdays_res):
                            potential_keywords.append((entry, current_word, key, "No Entries"))
                    check_percentage(entry, tweet_list, potential_keywords)


def check_percentage(topic, tweet_list, potential_keywords):
    #We need to try see if they relate to each other.
    #How many times do the words appear with each other.
    with open('file_to_write', 'a') as f:
        lets_test = []

        for entry in potential_keywords:
            for test in potential_keywords:
                #check tweet_list
                entries_combined_total = 0
                single = 0
                for tweet in tweet_list:
                    if (str(test[2]).lower() and str(entry[2]).lower()) in tweet.lower():
                        print ("--")
                        print (tweet.lower())
                        print (test[2].lower())
                        print (entry[2].lower())
                        print ("--")
                        entries_combined_total += 1
                        single += 1
                    elif (str(entry[2]).lower() in tweet.lower()):
                        single += 1
                lets_test.append((topic, entry[2],test[2],((entries_combined_total/single)*100)))
        f.write(str(lets_test)+"\n")
        f.close()
    return

def collect_todays_tweets(entry):

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
    print ("Started cleaning and median collection.")
    index = elastic_utils.list_all_indexes()
    for entry in index:

        if ("-latest") not in entry:
            if "-median" not in entry:
                #collect_todays_tweets(entry) #TODO commented out when testing
                get_median(entry)






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
        else:
            latest_tweets = ""
        index_dict[entry] = {"total": latest_entry_number, "last_entries": latest_tweets, 'current_entry': current_entry, 'last_entry': len(index_list),
                             }
        current_entry += 1
    return index_dict

def add_zeros(data, count):
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