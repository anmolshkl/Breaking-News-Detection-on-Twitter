import math
from tweet import Tweet

def isAscii(s):
    try:
        s.decode('ascii')
        return True
    except (UnicodeDecodeError, UnicodeEncodeError):
        return False

def qualified(msg, taglist, ignorelist, mintok):
    t = None
    if isAscii(msg):
        t = Tweet(msg,0,0,0)
    else:
        return False
    to = t.getTokens()
    return (len(to) >= mintok and not any(w in to for w in ignorelist))


def getEuclidNorm(vec):
    norm = 0
    for k,v in vec.iteritems():
        norm += math.pow(v, 2)

    return math.sqrt(norm)

def normalizeVector(vec):
    norm = getEuclidNorm(vec)
    for k,v in vec.iteritems():
        if norm != 0:
            vec[k] = vec[k] / norm
        else:
            vec[k] = 0

    return vec

def closestCossim(tweet, neighbors):
    bestT = None
    bestC = -2.0
    for n in neighbors:
        if tweet != n:
            c = computeCosineSim(tweet.getVector(), n.getVector())
            if c > bestC:
                bestT = n
                bestC = c

    return (bestT,bestC)

def computeCosineSim(v1, v2):
    dotProd = 0.0
    for k,v in v1.iteritems():
        if k in v2:
            dotProd += v1[k]*v2[k]

    norm = getEuclidNorm(v1) * getEuclidNorm(v2)
    cossim = 0.0
    if norm != 0:
        cossim = dotProd / norm

    return cossim
