import tweet
from collections import deque
import random

class Bucket:
    hashTable = {}
    def __init__(self, size):
        self.size = size

    def contains(self, hsh):
        return hsh in self.hashTable

    def getCollisions(self, hsh):
        if hsh in self.hashTable:
            return list(self.hashTable[hsh])
        else:
            return []

    def insertToBck(self, hsh, tweet):
        if hsh not in self.hashTable:
            self.hashTable[hsh] = deque([],maxlen=self.size)  #for O(1) queue operations
        self.hashTable[hsh].append(tweet)

class BucketsDB:
    bucketRndVec = []
    bucketList = []

    def __init__(self, L=0, k=0, size=0):
        self.L = L
        self.k = k
        self.size = size  # queue size

        for i in xrange(self.L):
            rndVecLst = []
            for j in xrange(self.k):
                rndVecLst.append([])
            BucketsDB.bucketRndVec.append(rndVecLst)
            BucketsDB.bucketList.append(Bucket(self.size))

    def updateRndVec(self, size):
        if size <= 0:
            return

        for bckt in xrange(self.L):
            for i in xrange(self.k):
                lst = BucketsDB.bucketRndVec[bckt][i]
                for index in xrange(size):
                    lst.append(random.gauss(0.0,1.0))

    def getPossibleNeighbors(self, tweet):
        poss = []
        rBcktCnt = 0

        for bck in BucketsDB.bucketList:
            vec = tweet.getVector()
            smallHsh = 0

            for i in xrange(self.k):
                dotProd = sum([v*BucketsDB.bucketRndVec[rBcktCnt][i][ky] for ky,v in vec.iteritems()])
                if dotProd >= 0:
                    smallHsh = smallHsh | (1 << i)
            rBcktCnt += 1
            poss += bck.getCollisions(smallHsh)
            bck.insertToBck(smallHsh, tweet)

        return poss
