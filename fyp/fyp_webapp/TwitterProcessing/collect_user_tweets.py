import tweepy
from fyp_webapp import config as cfg


def get_all_users_tweets(username):
    # authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(cfg.twitter_credentials["consumer_key"], cfg.twitter_credentials['consumer_secret'])
    auth.set_access_token(cfg.twitter_credentials['access_token'], cfg.twitter_credentials['access_token_secret'])
    api = tweepy.API(auth)

    # initialize a list to hold all the tweepy Tweets
    alltweets = []

    # make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name=username, count=200)

    # save most recent tweets
    alltweets.extend(new_tweets)

    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    count = 200

    # keep grabbing tweets until there are no tweets left to grab
    while (len(new_tweets) > 0 and count < 800):


        # all subsiquent requests use the max_id param to prevent duplicates
        print (username)
        print (oldest)
        print (count)
        try:
            new_tweets = api.user_timeline(screen_name=username, count=200, max_id=oldest)
        except:
            pass

        # save most recent tweets
        alltweets.extend(new_tweets)

        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        count = count + 200


    # transform the tweepy tweets into a 2D array that will populate the csv
    outtweets = [[tweet.id_str, tweet.created_at, tweet.text.encode("utf-8")] for tweet in alltweets]

    return alltweets