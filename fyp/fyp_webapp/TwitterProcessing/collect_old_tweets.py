from fyp_webapp.TwitterProcessing import got3 as got


def run():
    print("its here")
    def printTweet(descr, t):
        print (descr)
        print ("Username : %s" % t.username)
        print ("Retweets: %d" % t.retweets)
        print ("Text: %s" % t.text)
        print ("Mentions: %s" % t.mentions)
        print ("Hashtags: %s" % t.hashtags)
        print ("Time: %s" % t.date)
        print ("Formatted Time: %s\n" % t.formatted_date)

    #Example 1 - Get tweets by username
    tweetCriteria = got.manager.TweetCriteria().setUsername('barackobama').setMaxTweets(1)
    tweet = got.manager.TweetManager.getTweets(tweetCriteria)[0]

    printTweet("### Example 1 - Get tweets by username [barackobama]", tweet)

    #Example 2 - Get tweets by query searchp
    tweetCriteria = got.manager.TweetCriteria().setQuerySearch('Computer Security').setSince("2018-01-01").setUntil("2018-01-03").setMaxTweets(1)
    tweet = got.manager.TweetManager.getTweets(tweetCriteria)[0]

    printTweet("### Example 2 - Get tweets by query search [Computer Security]", tweet)


