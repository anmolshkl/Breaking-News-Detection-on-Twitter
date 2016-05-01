import math

'''
from sklearn import metrics
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

 
 Term Frequency(TF)        : the number of times that term t occurs in document d
 Inverse Doc Frequency(IDF): total number of documents/number of documents containing the term
'''

word_map    = {}
idf_map     = {}  
tf_map      = {}
avg_count   = {}
words_count = []
# suppose we got a list of strings 
tweet_count = 0
count       = 0

def getCentroid(tweet_list):

	for tweet in tweet_list:
		tweet_map = {}
		tweet     = tweet['sanitized_text'].split()
		words_count.append(0)
		for word in tweet:			
			words_count[tweet_count] += 1
			if word in word_map:  # if the word was seen before
				index = word_map[word]
				print(tf_map[index])
				print(tweet_count)
				if tweet_count in tf_map[index]:
					tf_map[index][tweet_count] += 1
				else:
					tf_map[index][tweet_count] = 1
				if word not in tweet_map:
					idf_map[index] += 1
					tweet_map[word] = 1
					
			else:  #if the word was not seen before
				word_map[word]             = count
				tf_map[count]              = {}
				tf_map[count][tweet_count] = 1
				idf_map[count]             = 1
				tweet_map[word]            = 1
				count                      += 1
		tweet_count += 1
	tf_idf_matrix = []
	totalTweets   = tweet_count
	tweet_count   = 0
	avg_score     = {}

	for tweet in tweet_list:
		dic       = {}
		tweet     = tweet['sanitized_text'].split()
		tweet_map = {}
		for word in tweet:
			if word not in tweet_map:
				tweet_map[word] = 1
				index = word_map[word]
				dic[index] = (tf_map[index][tweet_count]/words_count[tweet_count])*(1+math.log(totalTweets/idf_map[index]))
		tf_idf_matrix.append(dic)
		tweet_count += 1


	# get average tf-idf vector

	for vector in tf_idf_matrix:
		for k in vector:
			if k in avg_count:
				avg_count[k] += vector[k]
			else:
				avg_count[k] = vector[k]	

	for k in avg_count:
		avg_count[k] /= totalTweets

	# get centroid by cosine similarity
	
	max_score   = 0
	max_pos     = 0
	tweet_count = 0

	for vector in tf_idf_matrix:
		val = 0
		mag = 0
		for k in vector:
			val += vector[k]*avg_count[k]
			mag += vector[k]*vector[k]
		val = val/(math.sqrt(mag))
		if val > max_score:
			max_score = val
			max_pos = tweet_count
		tweet_count += 1

	return tweet_list[max_pos]
