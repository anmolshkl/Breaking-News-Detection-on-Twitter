import os
import json
import tweepy
import requests.packages.urllib3 as urllib3
import time
from tweet_schema import Tweet
import datetime
from mongoengine import *

'''
Takes the Tweet IDs(obtained from Twitter FSD, 
http://demeter.inf.ed.ac.uk/cross/docs/fsd_corpus.tar.gz) and retrieves the corresponding tweet 
objects if not present in the DB.
'''

total_tweets_retrieved = 0

def scrapeTweets():
    print 'entered scrapeTweets'
	# disable all HTTPS/TLS warnings
    urllib3.disable_warnings()

    global total_tweets_retrieved

    # load api keys from api_keys.json
    keys_file_path = os.path.join(os.path.dirname(__file__), os.pardir, 'api_keys.json')

    with open(keys_file_path) as api_keys:    
        keys = json.load(api_keys)

    # provide auth params & obtain an instance of API
    auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
    auth.set_access_token(keys['access_token'], keys['access_token_secret'])

    api = tweepy.API(auth)

    relevant_tweet_ids_path = os.path.join(os.path.dirname(__file__), os.pardir, 'Data/relevance_judgments')

    # connect to DB
    db = connect('Tweets')
    with open(relevant_tweet_ids_path) as relevant_tweet_ids:
        print 'opened relevance_judgments'
        t0 = time.time()
        for line in relevant_tweet_ids:
            status_obj = None
            tweet_id = line.split(" ")[0]
            tweets = Tweet.objects(tweet_id=tweet_id).all()
            # fetch tweet only if it doesnt exist
            if tweets.count() == 0:
                # if it doesn't exist, fetch from Twitter
                try:
                    print "Fetching tweet={0}".format(tweet_id)
                    status = api.get_status(tweet_id)
                    print status.id_str
                    total_tweets_retrieved      = total_tweets_retrieved + 1
                    tweet                       = Tweet()
                    tweet.tweet_id              = status.id_str
                    tweet.text                  = status.text
                    tweet.created_at            = status.created_at
                    tweet.in_reply_to_status_id = status.in_reply_to_status_id_str 
                    tweet.user_id               = status.user.id_str
                    tweet.user_name             = status.user.name
                    tweet.user_followers        = status.user.followers_count
                    tweet.user_location         = status.user.location
                    tweet.favourites_count      = status.user.favourites_count
                    if status.coordinates is not None:
                        tweet.coordinates       = status.coordinates['coordinates']
                    tweet.language              = status.lang
                    # tweet.place_coordinates   = status['']
                    tweet.retweet_count         = status.retweet_count
                    tweet.retweeted             = status.retweeted
                    # tweet.inserted_at
                    tweet.is_news               = True
                    tweet.save()
                except tweepy.RateLimitError:
                    print("Going to Sleep")
                    time.sleep(15 * 60)
                    print status.id_str
                except Exception as e:
                    print str(e)
            else:
                # if it does exist, then just label it as news
                for t in tweets:
                    t.is_news = True
                    t.save()
    print "Total Time={0}".format(time.time()-t0)
    print "Total Tweets={0}".format(total_tweets_retrieved)
if __name__ == "__main__":
    print 'run'
    scrapeTweets()
