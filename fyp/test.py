from fyp_webapp.ElasticSearch import elastic_utils
from fyp_webapp import config as cfg
from fyp_webapp.TwitterProcessing import preprocessor
from fyp_webapp.TwitterProcessing import termsfrequency
from fyp_webapp.TwitterProcessing import collect_old_tweets

res = elastic_utils.iterate_search("psn")
for entry in res:
    print ("The number of tweets for the 19th hour was: %s, and this was on: %s" % (str(entry["_source"]["hour_breakdown"]["19"]), str(entry["_source"]["date"])))


#print(collect_old_tweets.run(query_search="psn", start_date="2018-01-24", end_date="2018-01-25"))



#18:59:14