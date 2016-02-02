import json
import os
import tweepy
import chalk
import requests.packages.urllib3 as urllib3
import time
from tweet_schema import Tweet
from flask import Flask, render_template, send_from_directory
from mongoengine import *
import threading
from subprocess import call

'''
Takes the Tweet IDs(obtained from Twitter FSD, 
http://demeter.inf.ed.ac.uk/cross/docs/fsd_corpus.tar.gz) and retrieves the corresponding tweet 
objects.
'''

app = Flask(__name__)
app.config['DEBUG'] = False

# global vars
tweet_count        = 0
time_per_100       = []
avg_time_per_fetch = 0
fetch_count        = 0
TARGET             = 10000000

def scrapeTweets():
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

    global tweet_count

    global time_per_100

    global avg_time_per_fetch

    global fetch_count
    global TARGET

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
                    chalk.green("Scraped {0} tweets, Total ={1} tweets".format(
                        len(status_obj), tweet_count))
                except tweepy.RateLimitError:
                    chalk.blue("Going to Sleep")
                    time.sleep(15 * 60)
                finally:
                    t0 = time.time()
                    tweet_id_list[:] = []

            # Stop thread if no of tweets > 1,00,00,000
            if(fetch_count*100 > TARGET):
                print "Fetched All the Tweets"
                return


t = threading.Thread(target=scrapeTweets)

@app.route("/")
def main():
    db_tweets_count = len(Tweet.objects)
    est_time = (((10000000 - fetch_count*100) * avg_time_per_fetch) / 100)/60
    return render_template(
        'index.html',
        db_tweets_count=db_tweets_count,
        tweet_count=tweet_count,
        avg_time_per_fetch=avg_time_per_fetch,
        fetch_count=fetch_count,
        est_time=est_time,
        is_alive=t.isAlive(),
        target=TARGET
    )

@app.route("/download")
def downloadDB():
    return 'Currently Not Working'
    # root_dir = os.path.dirname(os.getcwd())
    # outfile = os.path.join(root_dir, os.pardir, 'static', os.pardir, 'tweet_db')
    # call(["mongodump", "-d","Tweets","-o",outfile],shell=True)
    # return send_from_directory(os.path.join(root_dir,'static'), 'tweet_db')

if __name__ == "__main__":
    
    t.start()
    app.run()
