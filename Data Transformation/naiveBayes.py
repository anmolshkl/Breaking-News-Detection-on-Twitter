from mongoengine import *
from random import shuffle
from pymongo import MongoClient
import numpy as np
from sklearn import metrics
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import cPickle
import os

client            = MongoClient()
db2               = client.dump
tweets            = {}
no_of_tweets      = 0
split			  = 0.6  # ratio in which to split dataset
accuracy		  = 0
count_vect        = None
clf               = None 
tfidf_transformer = None
project_root	  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_dump_path   = os.path.join(project_root, 'Classifier Models', 'Naive Bayes')

# return [[x1, x2, x3 ...], [y1, y2, y3 ...]]
def getData():
	global tweets
	global no_of_tweets
	count        = 0
	rec_count    = 0
	lmt          = 100000 # No of tweets to retrieve in one fetch
	no_of_tweets = db2.Labeled_Tweets.find().count()
	
	# get data for training...
	print "naiveBayes: Reading Database"
	while rec_count < no_of_tweets:
		cursor = db2.Labeled_Tweets.find({}, 
			{'_id':0, 'sanitized_text' : 1, 'is_news' :1}).skip(rec_count).limit(lmt)

		for record in cursor:
			tweet_list = []
			tweet_list.append(record['sanitized_text'])
			if record['is_news']:
				tweet_list.append(0)
			else:
				tweet_list.append(1)	
			tweets[count] = tweet_list
			count = count + 1
		rec_count += lmt
	print "naiveBayes: Read Database, fetched {0} tweets".format(no_of_tweets)

	keys =  list(tweets.keys())
	data = []
	target = []
	for key in keys:
		data.append(tweets[key][0])
		target.append(tweets[key][1])

	return [data, target]


# return a list of - CountVectorizer, TfidfTransformer, MultinomialNB model
def train(data, target):
	count   = 0
	matched = 0
	global split, accuracy, clf, tfidf_transformer, count_vect

	divider         = int(split * no_of_tweets)
	trainClassifier = {'data' : data[0:divider], 'target': target[0:divider]}
	category_names  = ['news', 'not news']

	### Training the Naive Bayes Classifier

	count_vect = CountVectorizer()
	X_train_counts = count_vect.fit_transform(trainClassifier['data'])
	print('naiveBayes: Transformed the sparse dataset')
	print(X_train_counts.shape)

	tfidf_transformer = TfidfTransformer()
	X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)

	clf = MultinomialNB().fit(X_train_tfidf, trainClassifier['target'])

	### Testing the Naive Bayes Classifier

	testClassifier = {'data' : data[divider:], 'target': target[divider:]}

	X_new_counts = count_vect.transform(testClassifier['data'])
	X_new_tfidf = tfidf_transformer.transform(X_new_counts)

	predicted = clf.predict(X_new_tfidf)

	for doc, category in zip(testClassifier['data'], predicted):
		if category == testClassifier['target'][count]:
			matched += 1
		count += 1	

	print(str("naiveBayes:  {0} are matched".format(matched)))
	accuracy = np.mean(predicted == testClassifier['target'])
	print "naiveBayes: Accuracy={0}".format(accuracy)

	return [count_vect, tfidf_transformer, clf]

def saveModel():

	if count_vect == None or tfidf_transformer == None or clf == None:
		print "naiveBayes: Error! Please generate model first"
	else:
		count_vect_file = 'count_vect.{0}_{1}.{2}.plk'.format(int(split*100), int(100-split*100), accuracy)
		tfidf_transformer_file = 'tfidf_transformer.{0}_{1}.{2}.plk'.format(int(split*100), int(100-split*100), accuracy)
		clf_file = 'clf.{0}_{1}.{2}.plk'.format(int(split*100), int(100-split*100), accuracy)

		with open(os.path.join(model_dump_path, count_vect_file), "wb") as fid:
			cPickle.dump(count_vect, fid)
		
		with open(os.path.join(model_dump_path, tfidf_transformer_file), "wb") as fid:
			cPickle.dump(tfidf_transformer, fid)
		
		with open(os.path.join(model_dump_path, clf_file), "wb") as fid:
			cPickle.dump(clf, fid)
		print "naiveBayes: Models saved!"


def getModel():
	[x, y]  = getData()
	return train(x, y)


if __name__ == '__main__':
	getModel()
	saveModel()