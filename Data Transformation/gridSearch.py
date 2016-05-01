from mongoengine import *
from random import shuffle
from pymongo import MongoClient
import numpy as np
from sklearn import metrics
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.grid_search import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from sklearn import metrics
from sklearn import svm

import cPickle
import os
from sklearn import linear_model

client            = MongoClient()
db2               = client.shuffled_DB2
tweets            = {}
no_of_tweets      = 0
split			  = 0.8  # ratio in which to split dataset
accuracy		  = 0
count_vect        = None
clf               = None 
tfidf_transformer = None
project_root	  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_dump_path   = os.path.join(project_root, 'Classifier Models', 'Naive Bayes')
text_clf_nb 	  = None
gs_clf			  = None


parameters = {'vect__ngram_range': [(1, 1), (1, 2)],
'tfidf__use_idf': (True, False),
'clf__alpha': (1e-2, 1e-3)}

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
				tweet_list.append(1)
			else:
				tweet_list.append(0)	
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
	global split, accuracy, clf, tfidf_transformer, count_vect, text_clf_nb, gs_clf

	divider         = int(split * no_of_tweets)
	trainClassifier = {'data' : data[0:divider], 'target': target[0:divider]}
	category_names  = ['news', 'not news']

	### Training the Naive Bayes Classifier
	print 'naiveBayes: Training on {0}% data'.format(split*100)

	text_clf_nb = Pipeline([('vect', CountVectorizer()),
		('tfidf', TfidfTransformer()),
		('clf', MultinomialNB())
		])

	text_clf_sgdc = Pipeline([('vect', CountVectorizer()),
		('tfidf', TfidfTransformer()),
		('clf', SGDClassifier(loss='log', penalty='l2',
			alpha=1e-3, n_iter=5, random_state=42)),
		])
	
	gs_clf = GridSearchCV(text_clf_nb, parameters, n_jobs=-1)

	gs_clf = gs_clf.fit(data[0:divider], target[0:divider])


	predicted = gs_clf.predict(data[divider:])

	test_target = target[divider:]

	for doc, category in zip(data[divider:], predicted):
		if category == test_target[count]:
			matched += 1
		count += 1	

	print(str("naiveBayes:  {0} are matched".format(matched)))
	accuracy = np.mean(predicted == test_target)
	print "naiveBayes: Accuracy={0}".format(accuracy)

	# find the best parameters
	best_parameters, score, _ = max(gs_clf.grid_scores_, key=lambda x: x[1])
	for param_name in sorted(parameters.keys()):
		print("%s: %r" % (param_name, best_parameters[param_name]))
	
	print(metrics.classification_report(test_target,
		predicted, labels=[0,1],
		target_names=['non news', 'news']))

	return [count_vect, tfidf_transformer, clf]

def saveModel():
	
	text_clf_nb_file = 'text_clf_nb|{0}_{1}|{2}.plk'.format(int(split*100), int(100-split*100), accuracy)

	with open(os.path.join(model_dump_path, text_clf_nb_file), "wb") as fid:
		cPickle.dump(text_clf_nb, fid)

	gs_clf_file = 'gs_clf|{0}_{1}|{2}.plk'.format(int(split*100), int(100-split*100), accuracy)
	
	with open(os.path.join(model_dump_path, gs_clf_file), "wb") as fid:
		cPickle.dump(gs_clf_file, fid)
	
	print "naiveBayes: Models saved!"


def getModel():
	[x, y]  = getData()
	return train(x, y)


if __name__ == '__main__':
	getModel()
	saveModel()
