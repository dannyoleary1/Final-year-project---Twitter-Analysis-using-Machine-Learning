#Import the necessary methods from tweetpy library
import tensorflow as tf
import tweepy
import json
from textblob import TextBlob
from nltk.tokenize import word_tokenize
import re
import preprocessor
#import fyp_webapp.ElasticSearch.elastic_utils as es
import fyp_webapp.config as cfg


class StreamListener(tweepy.StreamListener):

    def on_status(self, status):
        if hasattr(status, 'retweeted_status'):
            return #this filters out retweets
        elif (id<100000):
            dict = {"description":str(status.user.description), "loc":str(status.user.location), "text":str(status.text),"coords":str(status.coordinates),
                    "name": str(status.user.screen_name), "user_created":str(status.user.created_at), "followers":str(status.user.followers_count),
                    "id_str":str(status.id_str),"created":str(status.created_at), "retweets":str(status.retweet_count)}
            es.add_entry(cfg.twitter_credentials['topic'], id, dict)
            id += 1

    def on_error(self, status_code):
        print(status_code)
        if status_code == 420:
            return True

if __name__ == '__main__':

    # Authenticate
    auth = tweepy.OAuthHandler(cfg.twitter_credentials["consumer_key"], cfg.twitter_credentials['consumer_secret'])
    auth.set_access_token(cfg.twitter_credentials['access_token'], cfg.twitter_credentials['access_token_secret'])

    api = tweepy.API(auth)

    stream_listener = StreamListener()
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
    stream.filter(track=[cfg.twitter_credentials['topic']])

