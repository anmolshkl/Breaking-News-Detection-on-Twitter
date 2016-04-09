from tweet import Tweet
import math, utils


'''
 
 Term Frequency(TF)        : the number of times that term t occurs in document d
 Inverse Doc Frequency(IDF): total number of documents/number of documents containing the term

'''

class TfIdf:
    uniq_words     = {} # stores no of unique docs across which word is present
    pos_map        = {}     # stores unique words and their position in uniq_words map, across all tweets
    pos_in_map     = 0  # stores index available for new unique word
    num_prev_tweet = 1.0
    idfMap         = {}

    @classmethod
    def getVals(cls, tweet):
        before = len(cls.uniq_words)
        tfMap = {}      # stores frequency for a term in a tweet
        words = tweet.getTokens()
        for w in words:
            if w in tfMap:
                tfMap[w] += 1
            else:
                # when the word comes up for the first time, we 
                tfMap[w] = 1
                if w in cls.uniq_words:
                    cls.uniq_words[w] += 1
                else:
                    cls.uniq_words[w] = 1
                    cls.pos_map[w] = cls.pos_in_map
                    cls.pos_in_map += 1

        cls.num_prev_tweet += 1
        size_increase = len(cls.uniq_words) - before
        vec = {}

        for k,v in tfMap.iteritems():
            idf_score = 0
            if k in cls.idfMap:
                idf_score = cls.idfMap[k]  # get the score
                # update the score
                cls.idfMap[k] = math.log10((cls.num_prev_tweet) / (cls.uniq_words[k] + 1))
            else:
                idf_score = math.log10(cls.num_prev_tweet)
                cls.idfMap[k] = idf_score

            vec[cls.pos_map[k]] = v * idf_score

        vec = utils.normalizeVector(vec)

        tweet.setVector(vec)
        return size_increase