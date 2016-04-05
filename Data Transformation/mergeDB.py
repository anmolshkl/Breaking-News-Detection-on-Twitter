from mongoengine import *
from pymongo import MongoClient

''' merges the Non-news collection (Tweets.Tweets) with the News_db in a new db
    called Final_db (created by duplicating News_db)
'''

temp_list = []
from_db   = connect('Tweets')
client    = MongoClient()
to_db     = client.Final_db


if __name__ == "__main__":
	# read ALL documents
	print 'Reading all docs'
	cursor = from_db.Tweets.Tweets.find().limit(316823)
	# remove _id field
	print "Removing _id field"
	for record in cursor:
		record.pop("_id", None)
		temp_list.append(record)
	# insert documents
	print "Inserting ALL docs"
	to_db.Tweets.insert(temp_list)
	print "Done!"
	
