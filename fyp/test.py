import tweepy
from fyp_webapp import config as cfg

auth = tweepy.OAuthHandler(cfg.twitter_credentials["consumer_key"], cfg.twitter_credentials['consumer_secret'])
auth.set_access_token(cfg.twitter_credentials['access_token'], cfg.twitter_credentials['access_token_secret'])

api = tweepy.API(auth)

print("calls here")
print(tweepy.Cursor)
test = tweepy.Cursor(api.search, q="security", since="2018-01-23", until="2018-01-24").items()
for item in test:
    print (item)
for tweet in tweepy.Cursor(api.search, q="security", since="2018-01-01", until="2018-01-02").items():
    print("its here")
    print(tweet)