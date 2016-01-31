import json
import os
import tweepy

'''
Takes the Tweet IDs(obtained from Twitter FSD, 
http://demeter.inf.ed.ac.uk/cross/docs/fsd_corpus.tar.gz) and retrieves the corresponding tweet 
objects.
'''

# load api keys from api_keys.json
file = os.path.join(os.path.dirname(__file__),os.pardir, 'api_keys.json')

with open(file) as api_keys:    
    keys = json.load(api_keys)

# provide auth params & obtain an instance of API
auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
auth.set_access_token(keys['access_token'], keys['access_token_secret'])

api = tweepy.API(auth)

api.statuses_lookup