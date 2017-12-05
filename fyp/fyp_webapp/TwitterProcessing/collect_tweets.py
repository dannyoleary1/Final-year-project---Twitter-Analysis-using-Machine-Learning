#Import the necessary methods from tweetpy library
import tweepy
from fyp_webapp.ElasticSearch import elastic_utils as es
from fyp_webapp import config as cfg



class StreamListener(tweepy.StreamListener):

    def on_status(self, status):
        topic = cfg.twitter_credentials['topic']
        id = es.last_id(topic)
        if hasattr(status, 'retweeted_status'):
            return #this filters out retweets
        else:
            id += 1
            dict = {"description":str(status.user.description), "loc":str(status.user.location), "text":str(status.text),"coords":str(status.coordinates),
                    "name": str(status.user.screen_name), "user_created":str(status.user.created_at), "followers":str(status.user.followers_count),
                    "id_str":str(status.id_str),"created":str(status.created_at), "retweets":str(status.retweet_count)}
            print (id)
            es.add_entry(topic, id, dict)

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

def create_stream():
    auth = tweepy.OAuthHandler(cfg.twitter_credentials["consumer_key"], cfg.twitter_credentials['consumer_secret'])
    auth.set_access_token(cfg.twitter_credentials['access_token'], cfg.twitter_credentials['access_token_secret'])

    api = tweepy.API(auth)

    stream_listener = StreamListener()
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener)

    stream.filter(track=[cfg.twitter_credentials['topic_twitter']])
    return stream
