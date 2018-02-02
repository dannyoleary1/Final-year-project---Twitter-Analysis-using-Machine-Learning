from fyp_webapp.TwitterProcessing import got3 as got
from fyp_webapp.ElasticSearch import elastic_utils as es


def run(query_search, start_date, end_date, max_tweets=500000):
    print("its here")

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
    data = {}
    current_hour = 23
    current_tweet_count = 0
    for entry in tweet:
        if entry.date.hour == current_hour:
            current_tweet_count += 1
        else:
            data[current_hour] = current_tweet_count
            print ("--------------")
            print (current_hour)
            print (data[current_hour])
            print ("---------------")
            current_hour = current_hour-1
            current_tweet_count = 1

    data[current_hour] = current_tweet_count

    dict = {"date": str(start_date), "total": len(tweet), "last_time": tweet[len(tweet)-1].date, "hour_breakdown": data}
    id = es.last_id(topic)
    id += 1
    es.add_entry(topic, id, dict)
    print(id)
