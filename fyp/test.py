from fyp_webapp.ElasticSearch import elastic_utils
from fyp_webapp import config as cfg
from fyp_webapp.TwitterProcessing import preprocessor
from fyp_webapp.TwitterProcessing import termsfrequency
from fyp_webapp.TwitterProcessing import collect_old_tweets



print(collect_old_tweets.run(query_search="psn", start_date="2018-01-24", end_date="2018-01-25"))



#18:59:14