from tweet import Tweet
import math, utils


'''
 
 Term Frequency(TF)        : the number of times that term t occurs in document d
 Inverse Doc Frequency(IDF): total number of documents/number of documents containing the term

'''

class TfIdf:
    uniqWords = {} # stores unique words and their doc frequency, across all tweets
    posMap = {}     # stores unique words and their position in map, across all tweets
    posinmap = 0
    numprevtweet = 1.0
    idfMap = {}

    @classmethod
    def getVals(cls, tweet, oovMap):
        before = len(cls.uniqWords)
        tfMap = {}      # stores frequency for a term in a tweet
        words = tweet.getTokens()
        for w in words:
            # if w in oovMap:
            #     w = oovMap[w]
            if w in tfMap:
                tfMap[w] += 1
            else:
                tfMap[w] = 1
                if w in cls.uniqWords:
                    cls.uniqWords[w] += 1
                else:
                    cls.uniqWords[w] = 1
                    cls.posMap[w] = cls.posinmap
                    cls.posinmap += 1

        cls.numprevtweet += 1
        sizeIncrease = len(cls.uniqWords) - before
        vec = {}

        for k,v in tfMap.iteritems():
            idf_score = 0
            if k in cls.idfMap:
                idf_score = cls.idfMap[k]  # shouldn't this be after next line?
                cls.idfMap[k] = math.log10((cls.numprevtweet) / (cls.uniqWords[k] + 1))
            else:
                idf_score = math.log10(cls.numprevtweet)
                cls.idfMap[k] = idf_score

            vec[cls.posMap[k]] = v * idf_score

        vec = utils.normalizeVector(vec)

        tweet.setVector(vec)
        return sizeIncrease
