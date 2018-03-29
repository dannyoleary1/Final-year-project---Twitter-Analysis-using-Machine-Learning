from fyp_webapp.TwitterProcessing import got3 as got
from fyp_webapp.ElasticSearch import elastic_utils as es


def run(query_search, start_date, end_date, max_tweets=500000):

    def printTweet(descr, t):
        print(descr)
        print(type(t))
        print("Username : %s" % t.username)
        print("Retweets: %d" % t.retweets)
        print("Text: %s" % t.text)
        print("Mentions: %s" % t.mentions)
        print("Hashtags: %s" % t.hashtags)
        print("Time: %s" % t.date)
        print("Formatted Time: %s" % t.formatted_date)
        print("Geo info: %s\n" % t.geo)

    # Example 2 - Get tweets by query searchp
    topic = query_search
    tweetCriteria = got.manager.TweetCriteria().setQuerySearch(query_search).setSince(start_date).setUntil(
        end_date).setLang('eng').setMaxTweets(max_tweets)

    tweet = got.manager.TweetManager.getTweets(tweetCriteria)

    return tweet
