import os
import json
import tweepy
import requests.packages.urllib3 as urllib3
import time
from news_schema import News
import datetime
from mongoengine import *

'''
Takes the User IDs and retrieves tweets from User's Timeline.
'''

def getTweets():
    time_per_100       = []
    fetch_count        = 0
    avg_time_per_fetch = 0
    tweet_count        = 0
    modified_at        = None


    # disable all HTTPS/TLS warnings
    urllib3.disable_warnings()

    # load api keys from api_keys.json
    keys_file_path = os.path.join(os.path.dirname(__file__), 'api_keys_anmolchuck.json')

    with open(keys_file_path) as api_keys:    
        keys = json.load(api_keys)

    # provide auth params & obtain an instance of API
    auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
    auth.set_access_token(keys['access_token'], keys['access_token_secret'])

    api = tweepy.API(auth)

    # db_path = os.path.join(os.path.dirname(__file__), os.pardir, 'Data/tweet_ids') 

    # connect to DB
    db = connect('News_db')

    # drop the database once to ensure whenever the thread is run, we create the db afresh
    db.drop_database('News_db')
    t0 = time.time()
    no_of_tweets = 0
    total_no_of_tweets = 0
    user_id = [34908698,362051343,361501426,7905122,180306960,30857481,28370738,110458336,2883841,28172926,30261067,20562637,113050195,28140646,621523,35773039,15164565,15861355,44316192,44078873,15861220,1642135962,28137012,38400130,32355144,122097236,19230601,713993413,7302282,16877611,2557521,26257166,15110357,4898091,34713362,18949452,32359921,16334857,59736898,214007688,129834917,15108702,39817941,375721095,2424208849,506504366,242689065,116559622,23484039,18424289,64643056,115754870,134758540,6509832,267158021,29958928,15954704,19897138,37034483,36327407,20751449,3123883238,240649814,31632905,177829660,256495314,39743812,245687754,38647512,355989081,98362607,17710740,39240673,17469289,16973333,87818409,18071358,9763482,87416722,4970411,7587032,788524,14173315,612473,28785486,2467791,15012486,5988062,1367531,759251,428333,6017542,3108351,51241574,1652541,14293310,807095,742143,5402612]
    print "No of users={0}".format(len(user_id))

    last_id = [None for i in range(len(user_id))]
    number = 0
    rate_limit = 180
    no_of_requests = 0

    while(total_no_of_tweets < 3200 * len(user_id)):
        try:
            status_obj = api.user_timeline(user_id = user_id[number], count = 200, max_id = last_id[number])
            # print "fetched {0} tweets".format(len(status_obj))
            no_of_requests += 1
            for status in status_obj:
                tweet                       = News()
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
                no_of_tweets  = no_of_tweets + 1
                total_no_of_tweets = total_no_of_tweets + 1
                last_id[number] = tweet.tweet_id
                #print(tweet.user_name)
            # print "last id={0}".format(last_id[number])
            # print "total no of tweets {0}".format(no_of_tweets)
            if no_of_requests%100 == 0:
                    print "{0} tweets fetched".format(total_no_of_tweets)
                    
            if(no_of_tweets >= 3200):
                number += 1
                # if we have fetched tweets for every user, just return
                if number > len(user_id):
                    return
                number = number % len(user_id)
                print "moved to {0} user".format(number)
                no_of_tweets = 0

        except tweepy.RateLimitError:
            print("Going to Sleep")
            print no_of_requests
            t0 = time.time() - t0
            print(t0/60)
            print "sleeping for {0} sec".format(16*60 - t0)
            if t0 > 16*60:
                time.sleep(15*60) 
            else:
                time.sleep(16*60 - t0)
            t0 = time.time()
        except Exception as e:
            print("exception came")
            print(str(e))
            time.sleep(15 * 60)
    t0 = time.time() - t0
    t0 = t0/60
    print(t0)
    return

if __name__ == "__main__":
    getTweets()
