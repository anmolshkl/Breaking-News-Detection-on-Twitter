import os
os.environ['https_proxy']='http://172.31.16.10:8080'

from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from time import strftime
import sys
import json
import global_vars
import pika
import time

# The below keys can be gotten by creating an
# application on http://apps.twitter.com
ckey        = 'H8x9RBCEGbyTCBqUdVjxzmUDs'
csecret     = 'kf1R7kgq4zNgzhc3eggkXAxSTIUwPA9a9NoyYtfiS0xWNgSkwr'
atoken      = '835513550-cRrDufNgd93ZUhEbaZ8FCiZQZ1awSg5Ll1Qaau3j'
asecret     = 'jBoh0jl1W7N32W0FfAbXwuuLDJdmcrR90SGpFJMXv68hS'

# connect to Rabbitmq message queue
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel    = connection.channel()

# declare/create a queue if it doesn't exists
# ProjectName.Q.<Environment>.<ConsumerName>.MessageTypeName
channel.queue_declare(queue='FYP.Q.Filter.TweetMessage', durable=False)


class listener(StreamListener):
    num_of_tweets = 0
    tweet_list = []
    def on_data(self, data):
        decode = json.loads(data)
        stripped = {}
        user = {}
        if 'user' in decode:
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
            
            channel.basic_publish(exchange='',
                          routing_key='FYP.Q.Filter.TweetMessage',
                          body=json.dumps(stripped),
                          )
            
            if self.num_of_tweets % 10 == 0:
                sys.stdout.write("fetched " + str(self.num_of_tweets) + " tweets..." + '\n')

        return True

    def on_error(self, status):
        print >> sys.stderr, 'Encountered an error:', status
        
        if status == 420:
            print "Sleeping for 1 min"
            time.sleep(70)
            #returning False in on_data disconnects the stream
            return True

        return True # else keep stream alive

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Keeps stream alive

def run():
    auth = OAuthHandler(ckey, csecret)
    auth.set_access_token(atoken, asecret)
    try:
        twitterStream = Stream(auth, listener())
    except IncompleteRead:
        pass
    # Coordinates below is a bounding box roughly around New York City
    # twitterStream.filter(locations=[-74.2589, 40.4774, -73.7004, 40.9176])
    # Bounding box coordinates for India
    # https://en.wikipedia.org/wiki/User:The_Anome/country_bounding_boxes
    # locations=[65.000, 6.000, 97.350, 35.956 ], India
    # locations=[167.740, 8.732, 167.740, 8.732], USA
    # track=['news','breakingnews'], # we can't add location and track simultaneously 
        
    twitterStream.filter(track=['news','breakingnews'],languages=["en"], async=True)


if __name__ == "__main__":
	run()