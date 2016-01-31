#!/usr/bin/python

from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from time import strftime
import sys
import os
import json
import global_vars

# The below keys can be gotten by creating an
# application on http://apps.twitter.com
ckey        = 'H8x9RBCEGbyTCBqUdVjxzmUDs'
csecret     = 'kf1R7kgq4zNgzhc3eggkXAxSTIUwPA9a9NoyYtfiS0xWNgSkwr'
atoken      = '835513550-cRrDufNgd93ZUhEbaZ8FCiZQZ1awSg5Ll1Qaau3j'
asecret     = 'jBoh0jl1W7N32W0FfAbXwuuLDJdmcrR90SGpFJMXv68hS'
tweet_queue = global_vars.tweet_queue

class listener(StreamListener):
    num_of_tweets = 0
    tweet_list = []
    def on_data(self, data):
        decode = json.loads(data)
        stripped = {}
        user = {}
        global tweet_queue

        user["name"] = decode["user"]["name"]
        user["screenName"] = decode["user"]["screen_name"]
        user["following"] = decode["user"]["friends_count"]
        user["followers"] = decode["user"]["followers_count"]
        user["id"] = decode["user"]["id"]
        user["statusCount"] = decode["user"]["statuses_count"]

        stripped["user"] = user
        stripped["tweet"] = decode["text"]
        stripped["id"] = decode["id"]
        stripped["timestamp"] = decode["timestamp_ms"]
        stripped["hashtags"] = decode["entities"]["hashtags"]
        stripped["mentions"] = decode["entities"]["user_mentions"]
        stripped["retweetedUsingUI"] = decode["retweeted"]
        coordinates = decode["coordinates"]
        stripped["coordinates"] = coordinates

        self.num_of_tweets = self.num_of_tweets + 1

        # sys.stdout.write(json.dumps(decode) + '\n')
        # sys.stdout.write(json.dumps(stripped) + '\n')
        
        self.tweet_list.append(stripped) # append to this list for writing to file later
        tweet_queue.append(stripped) # inqueue tweet

        if self.num_of_tweets%100 == 0:
            with open("tweets.txt","a") as f:
                for tweet in self.tweet_list:
                    f.write(json.dumps(tweet) + '\n')
            self.tweet_list = []
        if self.num_of_tweets % 10 == 0:
            sys.stderr.write("fetched " + str(self.num_of_tweets) + " tweets..." + '\n')

        return True

    def on_error(self, status):
        print >> sys.stderr, 'Encountered an error:', status
        if status_code == 420:
            #returning False in on_data disconnects the stream
            return False

        return True # else keep stream alive

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Keeps stream alive

def run():
    auth = OAuthHandler(ckey, csecret)
    auth.set_access_token(atoken, asecret)
    twitterStream = Stream(auth, listener())
    # Coordinates below is a bounding box roughly around New York City
    # twitterStream.filter(locations=[-74.2589, 40.4774, -73.7004, 40.9176])
    # Bounding box coordinates for India
    twitterStream.filter(
        # locations=[-74.2589, 40.4774, -73.7004, 40.9176], # New York
        # locations=[65, 6, 97.35, 35.956], # India 
        track=['news','breakingnews','latest'], # we can't add location and track simultaneously
        languages=["en"],
        async=True
        )


