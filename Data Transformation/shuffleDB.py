from mongoengine import *
from random import shuffle
from pymongo import MongoClient
from itertools import izip_longest

def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return izip_longest(*args, fillvalue=fillvalue)

db = connect('shuffled_DB')

# drop the database once to ensure whenever the thread is run, we create the db afresh
db.drop_database('shuffled_DB')

client = MongoClient()
db2    = client.Tweets


# get data for training...

news_tweet_count     = 0   # no of fetched news tweets
misc_tweet_count     = 0   # no of fetched miscellaneous tweets
news_tweet_fetch_lmt = 99 # no of news tweets to be retrieved from DB at a time
misc_tweet_fetch_lmt = 59 # no of misc tweets to be retrieved from DB at a time
total_news_lmt       = 10070047 # total news tweets to be retrieved
total_misc_lmt       = 6070521  # total misc tweets to be retrieved
total_tweets         = [] # final list having all the tweets
tweet_id             = [] # a temp list to store IDs of chunk of news/misc tweets fetched
cursor 				 = None
group_size			 = 10000

while news_tweet_count < total_news_lmt and misc_tweet_count < total_misc_lmt and total_news_lmt - news_tweet_count > news_tweet_fetch_lmt and total_misc_lmt - misc_tweet_count > misc_tweet_fetch_lmt:
	cursor = db2.Tweets_data.find({}, {'_id':1}).sort("_id", -1).skip(news_tweet_count).limit(news_tweet_fetch_lmt)
	
	news_tweet_count += news_tweet_fetch_lmt
	
	# append news tweets to a temp list
	for record in cursor:
		tweet_id.append(record['_id'])
	
	cursor = db2.Tweets_data.find({}, {'_id':1}).sort("_id", 1).skip(misc_tweet_count).limit(misc_tweet_fetch_lmt)	
	
	misc_tweet_count += misc_tweet_fetch_lmt
	
	# append misc tweets to temp list
	for record in cursor:
		tweet_id.append(record['_id'])
	
	# shuffle the retrieved news+misc tweets
	shuffle(tweet_id)
	
	# for t in db2.Tweets_data.find({'_id' : {'$in': tweet_id}}):
	# 	print t['is_news']
	
	for tweet in tweet_id:
		total_tweets.append(tweet)
	
tweet_id = []

# fetch remaining news tweets
news_tweet_fetch_lmt = total_news_lmt - news_tweet_count
cursor = db2.Tweets_data.find({}, {'_id':1}).sort("_id", -1).skip(news_tweet_count).limit(news_tweet_fetch_lmt)
for record in cursor:
	tweet_id.append(record['_id'])


# fetch remaining misc tweets
misc_tweet_fetch_lmt = total_misc_lmt - misc_tweet_count
cursor = db2.Tweets_data.find({}, {'_id':1}).sort("_id", 1).skip(misc_tweet_count).limit(misc_tweet_fetch_lmt)
for record in cursor:
	tweet_id.append(record['_id'])


shuffle(tweet_id)

print("shuffled them")


for tweet in tweet_id:
	total_tweets.append(tweet)

print 'total_tweets prepared'
count = 0

#create groups of 10000 tweets, with each group as a seperate list
groups = grouper(total_tweets, group_size)

# insert tweets in a group, this is done to avoid single, slow, batch insert
temp_list = []
for group in groups:
	cursor = db2.Tweets_data.find({'_id' : {'$in': group}})
	count += cursor.count(with_limit_and_skip=True)
	for record in cursor:
		record.pop("_id", None)
		temp_list.append(record)
	shuffle(temp_list)
	db.shuffled_DB.Labeled_Tweets.insert(temp_list)
	print(str("{0} are updated".format(count)))
	temp_list = []