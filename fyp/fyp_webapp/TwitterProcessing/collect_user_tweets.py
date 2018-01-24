import tweepy
from fyp_webapp import config as cfg


def get_all_users_tweets(username):
    # authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(cfg.twitter_credentials["consumer_key"], cfg.twitter_credentials['consumer_secret'])
    auth.set_access_token(cfg.twitter_credentials['access_token'], cfg.twitter_credentials['access_token_secret'])
    api = tweepy.API(auth)