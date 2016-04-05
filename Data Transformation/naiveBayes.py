from mongoengine import *
from random import shuffle
from pymongo import MongoClient
import numpy as np
from sklearn import metrics
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import cPickle

client = MongoClient()
db2 = client.dump

count = 0
rec_count = 0
lmt = 100000
no_of_tweets = db2.Labeled_Tweets.find().count()
tweets = {}

# get data for training...

while rec_count < no_of_tweets:
	cursor = db2.Labeled_Tweets.find({}, {'_id':0, 'sanitized_text' : 1, 'is_news' :1}).skip(rec_count).limit(lmt)

	for record in cursor:
		lis = []
		lis.append(record['sanitized_text'])
		if record['is_news']:
			lis.append(0)
		else:
			lis.append(1)	
		tweets[count] = lis
		count = count + 1
	rec_count += lmt

print("fetched all the news related tweets")


keys =  list(tweets.keys())

data = []
target = []

for key in keys:
	data.append(tweets[key][0])
	target.append(tweets[key][1])


divider = int(0.9 * no_of_tweets)
print divider
trainClassifier = {'data' : data[0:divider], 'target': target[0:divider]}
category_names = ['news', 'not news']


### Training the Naive Bayes Classifier

count_vect = CountVectorizer()
print('Created the object of the vectorizer')
X_train_counts = count_vect.fit_transform(trainClassifier['data'])
print('Transformed the sparse dataset')
print(X_train_counts.shape)

tfidf_transformer = TfidfTransformer()
print('Created the object of the transformer')
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
print('Transformed the tf-idf vector')
print(X_train_tfidf.shape)

clf = MultinomialNB().fit(X_train_tfidf, trainClassifier['target'])

### Testing the Naive Bayes Classifier

testClassifier = {'data' : data[divider:], 'target': target[divider:]}

X_new_counts = count_vect.transform(testClassifier['data'])
X_new_tfidf = tfidf_transformer.transform(X_new_counts)

predicted = clf.predict(X_new_tfidf)

matched = 0
count = 0

for doc, category in zip(testClassifier['data'], predicted):
	if category == testClassifier['target'][count]:
		matched += 1
	count += 1	

print(str("{0} are matched".format(matched)))
print(np.mean(predicted == testClassifier['target']))

# save the classifier
with open('naive_bayes_classifier_90_10.pkl', 'wb') as fid:
    cPickle.dump(clf, fid)    