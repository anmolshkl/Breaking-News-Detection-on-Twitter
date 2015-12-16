#!/usr/bin/python

from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from time import strftime
import sys
import os
import json

# The below keys can be gotten by creating an
# application on http://apps.twitter.com
ckey = ''
csecret = ''
atoken = ''
asecret = ''

class listener(StreamListener):
    num_of_tweets = 0
    def on_data(self, data):
        decode = json.loads(data)
        stripped = {}
        user = {}

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

        sys.stdout.write(json.dumps(stripped) + '\n')
        if self.num_of_tweets % 10 == 0:
            sys.stderr.write("fetched " + str(self.num_of_tweets) + " tweets..." + '\n')

        return True

    def on_error(self, status):
        print >> sys.stderr, 'Encountered an error:', status
        return True # Keeps stream alive

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Keeps stream alive

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
twitterStream = Stream(auth, listener())
# Coordinates below is a bounding box roughly around New York City
twitterStream.filter(locations=[-74.2589, 40.4774, -73.7004, 40.9176])

