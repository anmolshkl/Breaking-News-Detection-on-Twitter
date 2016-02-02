from mongoengine import *
import datetime

class Tweet(Document):
	tweet_id              = StringField(required=True)
	text                  = StringField(max_length=200, required=True)
	in_reply_to_status_id = StringField(max_length=200, default=None)
	user_id               = StringField(required=True)
	user_name             = StringField(max_length=200)
	user_followers        = IntField(default=0)
	created_at            = DateTimeField(required=True)
	user_location         = StringField(max_length=200, default='na') # eg Washington, USA
	favourites_count      = IntField(default=0)
	coordinates           = GeoPointField() # tweet location obtained from devie 
	language              = StringField(default=None)
	place_coordinates     = ListField(GeoPointField(), default=None) # place associated with tweet,a bounding box
	retweet_count         = IntField(default=0)
	retweeted             = BooleanField(default=False)
	inserted_at           = DateTimeField(default=datetime.datetime.now())
	meta                  = {'collection': 'Tweets'}
