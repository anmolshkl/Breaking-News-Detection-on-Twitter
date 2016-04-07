import os
import json
import tweepy
import requests.packages.urllib3 as urllib3
import time
from tweet_schema import Tweet
import datetime
from mongoengine import *

'''
Takes the User IDs and retrieves tweets from User's Timeline.
'''

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def getTweets():
    time_per_100       = []
    fetch_count        = 0
    avg_time_per_fetch = 0
    tweet_count        = 0
    modified_at        = None


    # disable all HTTPS/TLS warnings
    urllib3.disable_warnings()

    # load api keys from api_keys.json
    keys_file_path = os.path.join(project_root, 'Key', 'api_keys.json')

    with open(keys_file_path) as api_keys:    
        keys = json.load(api_keys)

    # obtain multiple instances of Twitter API to circumvent rate limit
    authList = []
    apiList  = []
    for i in range(len(keys)):
        authList[i] = tweepy.OAuthHandler(keys[i]['consumer_key'], keys[i]['consumer_secret'])
        authList[i].set_access_token(keys[i]['access_token'], keys[i]['access_token_secret'])
        apiList[i] = tweepy.API(authList[i])

    # db_path = os.path.join(os.path.dirname(__file__), os.pardir, 'Data/tweet_ids') 

    # connect to DB
    db = connect('Shit_db')

    # drop the database once to ensure whenever the thread is run, we create the db afresh
    db.drop_database('Shit_db')
    t0 = time.time()
    no_of_tweets = 0
    total_no_of_tweets = 0

    # news channel IDs
    # user_id = [34908698,362051343,361501426,7905122,180306960,30857481,28370738,110458336,2883841,28172926,30261067,20562637,113050195,28140646,621523,35773039,15164565,15861355,44316192,44078873,15861220,1642135962,28137012,38400130,32355144,122097236,19230601,713993413,7302282,16877611,2557521,26257166,15110357,4898091,34713362,18949452,32359921,16334857,59736898,214007688,129834917,15108702,39817941,375721095,2424208849,506504366,242689065,116559622,23484039,18424289,64643056,115754870,134758540,6509832,267158021,29958928,15954704,19897138,37034483,36327407,20751449,3123883238,240649814,31632905,177829660,256495314,39743812,245687754,38647512,355989081,98362607,17710740,39240673,17469289,16973333,87818409,18071358,9763482,87416722,4970411,7587032,788524,14173315,612473,28785486,2467791,15012486,5988062,1367531,759251,428333,6017542,3108351,51241574,1652541,14293310,807095,742143,5402612]
    
    # non news channel IDs
    user_id = [79708561,281766200,785493949,250205792,180463340,3060210854,2305049443,273181052,2463499796,71876190,26642006,92367751,259379883,399428964,26565946,24494557,166739404,52551600,25365536,15485441,15846407,14234323,125481462,27042513,133880286,243284052,44588485,51376979,27260086,17919972,18625669,16409683,21447363,58135085,23375688,92724677,30973,50374439,48410093,57928790,87170183,102957248,108391251,120998613,115622213,113419517,6463042,94775494,131975194,97865628,79915337,332188446,41067945,197150180,78022296,31348594,902534288,108253263,63390627,145125358,78242874,468479147,36057824,34464376,111871312,152251488,121677709,38403110,21787625,494747331,94163409,44849431,18872373,105710210,148248527,38479920,508932270,183230911,186388502,101311381,70652594,2719753171,23976386,23002923,33868638,16548023,40453512,18681139,279449435,144755081,132385468,54829997,266714730,108252113,3138637447,1111706414,61755650,14120922,216447259,129786468]
    print "No of users={0}".format(len(user_id))
    
    last_id        = [None for i in range(len(user_id))]
    number         = 0
    rate_limit     = 180
    no_of_requests = 0
    tweet_list     = []
    k              = 0 # current_api_index
    api_wait_end_time  = time.time() # stores timestamp till when the first API might have to wait

    while(total_no_of_tweets < 3200 * len(user_id)):
        try:
            status_obj = apiList[k].user_timeline(user_id = user_id[number], count = 200, max_id = last_id[number])
            # print "fetched {0} tweets".format(len(status_obj))
            no_of_requests += 1
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
                tweet.is_news               = True
                # tweet.save()
                tweet_list.append(tweet)
                no_of_tweets  = no_of_tweets + 1
                total_no_of_tweets = total_no_of_tweets + 1
                last_id[number] = tweet.tweet_id
                #print(tweet.user_name)
            # print "last id={0}".format(last_id[number])
            # print "total no of tweets {0}".format(no_of_tweets)
            if no_of_requests%100 == 0:
                    print "{0} tweets fetched".format(total_no_of_tweets)
                    
            if(no_of_tweets >= 3200):
                print "Saving Tweets to DB"
                # save tweets to db
                Tweet.objects.insert(tweet_list)
                tweet_list = []
                number += 1

                # if we have fetched tweets for every user, just return
                if number > len(user_id):
                    return
                number = number % len(user_id)
                print "moved to {0} user".format(number)
                no_of_tweets = 0

        except tweepy.RateLimitError:
            print "Saving Tweets to DB"
            # save tweets to db
            Tweet.objects.insert(tweet_list)
            tweet_list = [] 
            if k == len(apiList) - 1:
                if api_wait_end_time < time.time():
                    # we dont need to wait, so pass
                    pass
                else:
                    sleep_time = api_wait_end_time - time.time()
                    print "create_db: sleeping for {0} seconds".format(sleep_time)
                    time.sleep(sleep_time)
            k = (k + 1) % len(apiList)
            if k == 0:
                # update api_wait_end_time
                api_wait_end_time = time.time() + 15*60

            # print("Going to Sleep")
            # print no_of_requests
            # t0 = time.time() - t0
            # if t0 > 16*60:
            #     print "sleeping for {0} sec".format(15*60) 
            #     time.sleep(15*60) 
            # else:
            #     print "sleeping for {0} sec".format(16*60 - t0)
            #     time.sleep(16*60 - t0)
            # t0 = time.time()

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
