import utils

'''
This class is simply a container for the most recent 
size tweets to be processed by the system
'''
class RecentTweets:
    recentTweets = []
    def __init__(self, size):
        self.size = size

    '''
    The getClosestNeighbor method traverses the list, computing
    the cosine similarity between the supplied tweet and each of the tweets in the
    list, returning the tweet with the highest cosine similarity.
    '''
    def getClosestNeighbor(self,tweet):
        if len(RecentTweets.recentTweets) == 0:
            return (None,-2.0)

        v1 = tweet.getVector()
        closest = (None,-2.0)

        for t in RecentTweets.recentTweets:
            v2 = t.getVector()
            sim = utils.computeCosineSim(v1,v2)
            if  sim > closest[1]:
                closest = (t,sim)

        return closest

    def insert(self,tweet):
        if len(RecentTweets.recentTweets)==self.size:
            RecentTweets.recentTweets = RecentTweets.recentTweets[1:]

        RecentTweets.recentTweets.append(tweet)