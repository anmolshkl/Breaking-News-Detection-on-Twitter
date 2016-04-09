import tweet
from collections import deque
import random

class Bucket:
    '''
    The Bucket class is an object which encapsulates a hash table. 
    It has methods for insertion and retrieval.
    '''
    hash_table = {}
    def __init__(self, size):
        self.size = size

    def contains(self, hsh):
        return hsh in self.hash_table

    def getCollisions(self, hsh):
        if hsh in self.hash_table:
            return list(self.hash_table[hsh])
        else:
            return []

    def insertToBck(self, hsh, tweet):
        if hsh not in self.hash_table:
            self.hash_table[hsh] = deque([],maxlen=self.size)  #for O(1) queue operations
        self.hash_table[hsh].append(tweet)

class BucketsDB:
    '''
    The BucketsDB class is an object which encapsulates all the different buckets 
    and takes care of hashing.
    '''
    bucket_rndm_vec = []  # stores K random vectors for every Bucket/Hash Table
    bucket_list = []  # stores Bucket object/Hash Table object for every L bucket

    def __init__(self, L=0, k=0, size=0):
        self.L = L
        self.k = k
        self.size = size  # queue size

        for i in xrange(self.L):
            random_vectors = []
            for j in xrange(self.k):
                random_vectors.append([])

            # append random vectors
            BucketsDB.bucket_rndm_vec.append(random_vectors) 
            # create and append new Bucket object foor L Hash Tables
            BucketsDB.bucket_list.append(Bucket(self.size)) 

    def updateRndVec(self, size):
        ''' 
        Increases the size of all the random vectors by "size" 
        ie no of unique words(dimensions) encountered
        '''
        if size <= 0:
            return

        for bckt in xrange(self.L):
            for i in xrange(self.k):
                lst = BucketsDB.bucket_rndm_vec[bckt][i]
                for index in xrange(size):
                    lst.append(random.gauss(0.0,1.0))

    def getPossibleNeighbors(self, tweet):
        poss = []
        r_bckt_count = 0

        for bck in BucketsDB.bucket_list:
            vec = tweet.getVector()
            small_hash = 0

            for i in xrange(self.k):
                dotProd = sum([v*BucketsDB.bucket_rndm_vec[r_bckt_count][i][ky] for ky,v in vec.iteritems()])
                if dotProd >= 0:
                    small_hash = small_hash | (1 << i)
            r_bckt_count += 1
            poss += bck.getCollisions(small_hash)
            bck.insertToBck(small_hash, tweet)

        return poss
