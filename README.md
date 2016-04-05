# Breaking News Detection & Analysis on Twitter


## Introduction

Discover news as the events they are describing are unfolding, by using tweets posted by Twitter users. If successful, this should enable us to discover breaking news such as natural disasters, political unrest and big happenings in real-time. This, in turn, could lead to more efficient disaster relief. 

### What are the sub-problems?
1. Find those tweets that are news relevant in near real-time
2. Given a set of tweets concerning the same event, decide which of them is the most representative of the set
3. Geo-tagging tweets to see their reach and local/global effect (T)
4. Sentimental Analysis on the crowd response to the events that tweets describe (T)

## Data Set

The Twitter Streaming API is used for the puprose of collecting tweets in real-time. However, for evaluating our system, we need to maintain a 'static' data (stored tweets from Streaming API) and not real-time dynamic data (Streaming API) so that we can generate results which are comprarable.

For the purpose of building training/testing dataset for machine learning based classification algorithm (like Naive Bayes), we followed prominent news channels to gather News tweets and other gossip channels/individuals for personal/opinionated tweets. The database consisted of only 0.6 million tweets due rigorous limits set by Twitter.

## Steps Involved

### STEP 1: Filtering Tweets
Twitter's Streaming API generates a plethora of tweets. A majority of the tweets are not of any use to us (personal, spam, ad opinionated tweets). Hence, we have trained a Naive Bayes classifier using the training dataset to filter out the non-news tweets.

### STEP 2: Pre-processing
1. Cleaning - removing URLs, emoji's etc to give 'sanitized_text'
2. Tokenization
3. Stemming and Stop word removal


### STEP 3: Clustering - Locality Sensitive Hashing
<b>Locality sensitive hashing</b> (LSH) Indyk and Motwani [1998] is a technique for finding the nearest neighbor document in vector space utilizing vectors of random values and representing hyperplanes to generate hashes. This approach reduces the time and space complexity when finding the nearest neighbor.

LSH hashes the input items using k hyperplanes. Increasing the value of k decreases the probability of collision between non-similar items, while at the same time decreasing the probability of collision between nearest neighbors. To alleviate this, the implementation contains L different hash tables, each with independently chosen random hyperplanes. These hash tables are also called “buckets”. This increases the probability of the item colliding with its nearest neighbor in at least one of the L hash tables. In addition to using LSH to detect breaking news, we want to examine if named-entity recognition can improve the results we get from using LSH to filter tweets.

<b>Named-entity recognition</b> (NER) is a type of natural language processing (NLP). NLP refers to research that explore how computers can be utilized to understand, interpret, and manipulate natural languages, such as text and speech

The tweets are run through NER engine for this.

Experimenting using LSH & NER
There are several important parameters that can be varied to get different results.
Some of them are:
- MIN_COSSIM_FOR_EXISTING - leat cosine similarity between tweet and its neighbor for it to be added to the same
cluster
- MIN_ENTROPY - information entropy should be at least this much 
- MIN_TOKENS - no of minimum tokens after sanitizing tweets
- IGNORE - ignore tweets which contain words from this list
- MIN_TWEETS_IN_SLICE - . A cluster must have had at least these many tweets added to it during the current window to be printed
- MIN_UNIQUES - how many unique users must have tweets in a cluster for it be to qualified
- WINDOW_SIZE_IN_SECONDS - time between first tweet and current tweet, after which - all stories matching certain parameters will be printed

### STEP 4: Find the most representative news tweet
In order to find the most representative tweet(s) in a given cluster, they used a straightforward algorithm, as described in Rosa et al. [2011]. This algorithm is based on the use of centroids. It works by first calculating the tf-idf weights for each term in the cluster. When doing this, all tokens are turned into lower case representations, and any punctuation removed. Additionally, URLs are ignored when calculating these weights. After this a centroid is created based on these weights. This is done by taking the average of the tf-idf weights for each term. Once this is done, the cosine similarity is calculated between the centroid and each tweet in the cluster. The tweet with the highest cosine similarity is returned.
