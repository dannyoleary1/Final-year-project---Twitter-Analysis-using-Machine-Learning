from fyp_webapp.ElasticSearch import elastic_utils
from fyp_webapp import config as cfg
from fyp_webapp.TwitterProcessing import preprocessor
from fyp_webapp.TwitterProcessing import termsfrequency
from fyp_webapp.TwitterProcessing import collect_old_tweets
import string
import nltk
from nltk.corpus import stopwords
from collections import Counter

# res = elastic_utils.iterate_search("psn")
# for entry in res:



tweet = collect_old_tweets.run(query_search="psn", start_date="2018-01-26", end_date="2018-01-27")

results = []
for entry in tweet:
    print(entry.text)
    results.append(preprocessor.filter_multiple(str(entry.text), ats=True, stopwords=True, stemming=True, urls=True))
count_word_frequency = Counter()
for entry in results:
        print("-----------")
        print(entry)
        print(type(entry))
        print("-----------")
        terms_all = [term for term in entry]
        count_word_frequency.update(terms_all)
print(count_word_frequency.most_common(75))

#data = {}
#current_hour = 23
#current_tweet_count = 0
#for entry in tweet:
#    if entry.date.hour == current_hour:
#        current_tweet_count += 1
#    else:
#        data[current_hour] = current_tweet_count
#        print("--------------")
#        print(current_hour)
#        print(data[current_hour])
#        print("---------------")
 #       current_hour = current_hour - 1
 #       current_tweet_count = 1

#data[current_hour] = current_tweet_count

#dict = {"date": str(start_date), "total": len(tweet), "last_time": tweet[len(tweet) - 1].date, "hour_breakdown": data}
#id = es.last_id(topic)
#id += 1
#es.add_entry(topic, id, dict)
#print(id)



# 18:59:14
