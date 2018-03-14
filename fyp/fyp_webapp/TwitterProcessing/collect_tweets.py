#Import the necessary methods from tweetpy library
import tweepy
from fyp_webapp.ElasticSearch import elastic_utils as es
from fyp_webapp import config as cfg
from http.client import IncompleteRead
from fyp_webapp.tasks import aggregate_words



class StreamListener(tweepy.StreamListener):

    def on_status(self, status):
        if hasattr(status, 'retweeted_status'):
            return #this filters out retweets
        else:
            dict = {"description":str(status.user.description), "loc":str(status.user.location), "text":str(status.text),"coords":str(status.coordinates),
                    "name": str(status.user.screen_name), "user_created":str(status.user.created_at), "followers":str(status.user.followers_count),
                    "id_str":str(status.id_str),"created":str(status.created_at), "retweets":str(status.retweet_count)}
            aggregate_words.delay(dict)



    def on_error(self, status_code):
        print(status_code)
        if status_code == 420:
            return True

"""This checks if the topic in question has a space or not. This is important for aggregations to ElasticSearch."""
def check_topic_index(topic):
    if (" " in topic):
        return topic.replace(" ", "")
    else:
        return topic

def create_stream(topics, end_loop=False):
    auth = tweepy.OAuthHandler(cfg.twitter_credentials["consumer_key"], cfg.twitter_credentials['consumer_secret'])
    auth.set_access_token(cfg.twitter_credentials['access_token'], cfg.twitter_credentials['access_token_secret'])

    api = tweepy.API(auth)

    stream_listener = StreamListener()
    while end_loop is False:
        stream = tweepy.Stream(auth=api.auth, listener=stream_listener, timeout=60, async=True)
        try:
            stream.filter(languages=["en"], track=topics)
        except Exception as e:
            print ("----------------")
            print ("Error. Restarting Stream.... Error: ")
            print (e)
            print("----------------")

    return stream
