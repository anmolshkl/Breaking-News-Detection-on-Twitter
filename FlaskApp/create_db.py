import os
import json
import tweepy
import chalk
import requests.packages.urllib3 as urllib3
import time
from tweet_schema import Tweet
import datetime
from mongoengine import *
import redis

'''
Takes the Tweet IDs(obtained from Twitter FSD, 
http://demeter.inf.ed.ac.uk/cross/docs/fsd_corpus.tar.gz) and retrieves the corresponding tweet 
objects.
'''
r = redis.StrictRedis(host='localhost', port=6379, db=0)

def scrapeTweets():
    time_per_100       = []
    fetch_count        = 0
    avg_time_per_fetch = 0
    tweet_count        = 0
    target             = 1000000
    modified_at        = None


    # disable all HTTPS/TLS warnings
    urllib3.disable_warnings()

    # load api keys from api_keys.json
    keys_file_path = os.path.join(os.path.dirname(__file__), os.pardir, 'api_keys.json')

    with open(keys_file_path) as api_keys:    
        keys = json.load(api_keys)

    # provide auth params & obtain an instance of API
    auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
    auth.set_access_token(keys['access_token'], keys['access_token_secret'])

    api = tweepy.API(auth)

    db_path = os.path.join(os.path.dirname(__file__), os.pardir, 'Data/tweet_ids')

    # connect to DB
    db = connect('Tweets')

    # drop the database once to ensure whenever the thread is run, we create the db afresh
    db.drop_database('Tweets')

    tweet_id_list = []

    

    with open(db_path) as file_db:
        t0 = time.time()
        for line in file_db:
            status_obj = None
            tweet = line.split("\t")[0]
            tweet_id_list.append(tweet)
            if(len(tweet_id_list) == 100):
                try:
                    status_obj = api.statuses_lookup(tweet_id_list, [False], [False], [True])
                    for status in status_obj:
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
                        tweet.save()
                    t1 = time.time()
                    time_per_100.append(t1-t0)
                    fetch_count = fetch_count + 1
                    avg_time_per_fetch = sum(time_per_100)/len(time_per_100)
                    chalk.red('Avg time per fetch = {0}'.format(avg_time_per_fetch))
                    tweet_count += len(status_obj)
                    modified_at = datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')
                    print time_per_100
                    chalk.green("Scraped {0} tweets, Total ={1} tweets".format(
                        len(status_obj), tweet_count))

                    # save all the stats to REDIS
                    r.set('tweet_count', tweet_count)
                    r.set('avg_time_per_fetch', avg_time_per_fetch)
                    r.set('fetch_count', fetch_count)
                    r.set('modified_at', modified_at)
                    # r.set('target', target) 

                except tweepy.RateLimitError:
                    chalk.blue("Going to Sleep")
                    time.sleep(15 * 60)
                finally:
                    t0 = time.time()
                    tweet_id_list[:] = []

            # Stop thread if no of tweets > 1,00,00,000
            if(fetch_count*100 > target):
                print "Fetched All the Tweets"
                return


if __name__ == "__main__":
    scrapeTweets()