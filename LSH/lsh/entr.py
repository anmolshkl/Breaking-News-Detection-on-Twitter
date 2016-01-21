from __future__ import division
import sys, json, string, math

def getTokens(s):
    tokens = []
    for t in s.lower().split():
        if not ('http' in t or t.startswith('#') or t.startswith('@')):
            t = t.translate({ord(c): None for c in string.punctuation})
            if len(t) > 0:
                tokens.append(t)
    return tokens

def getEntropy(d):
    words = getTokens(d['first'][1])
    l = 0
    hist = {}
    elist = []
    for i in [t[1] for t in d['tweets']]:
        words += getTokens(i)
    for e in words:
        l += 1
        if e not in hist:
            hist[e] = 0
        hist[e] += 1
    for v in hist.values():
        c = v / l
        elist.append(-c * math.log(c, 2))
    return sum(elist)

