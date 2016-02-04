from mongoengine import *
import datetime

class Stats(Document):
	tweet_count        = IntField(required=True)
	time_per_100       = DecimalField(required=True, precision=6)
	avg_time_per_fetch = DecimalField(required=True, precision=6)
	fetch_count        = IntField(required=True)
	target             = IntField(required=True)
	modified_at        = DatDateTimeField(default=datetime.datetime.now())
	meta               = {'collection': 'Stats'}
