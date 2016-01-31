import utils

class RecentTweets:
    recentTweets = []
    def __init__(self, size):
        self.size = size

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
