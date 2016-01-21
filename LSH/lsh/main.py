from tweet import Tweet
from tfidf import TfIdf
from recenttweets import RecentTweets
from buckets import Bucket, BucketsDB
from datetime import datetime
from operator import itemgetter
import sys, json, utils, math
import stream
import get_stories
import threading, collections, Queue
import global_vars

print 'start 1'
# start fetching the tweets and queue them up
stream.run()

print 'start 2'
L             = 36
K             = 13
QUEUE_SIZE    = 20
RECENT_TWEETS = 2000
MIN_TOKENS    = 2

IGNORE = ['i', 'im', 'me', 'mine', 'you', 'yours']

TAGS   = ['#news','#breakingnews']

oovMap = {}

buckets = BucketsDB(L, K, QUEUE_SIZE)
recent  = RecentTweets(RECENT_TWEETS)

unprocessed_tweet_queue = global_vars.tweet_queue 
processed_tweet_queue   = global_vars.processed_tweet_queue

def getClosestNeighborBuckets(tweet):
    poss = buckets.getPossibleNeighbors(tweet)
    aggr = {}
    look = {}
    for e in poss:
        if e.msgid in aggr:
            aggr[e.msgid] += 1
        else:
            aggr[e.msgid] = 1
            look[e.msgid] = e
    neigh = sorted(aggr.iteritems(), key=itemgetter(1), reverse=True)
    neigh = [z[0] for z in neigh[:min(len(neigh),(3*L))]]
    neigh = [look[k] for k in neigh]
    return utils.closestCossim(tweet, neigh)

def getClosestNeighborRecent(tweet, cosBuck):
    close = (None,-2.0)
    if ((1-cosBuck) >= 0.5):
        close = recent.getClosestNeighbor(tweet)
    recent.insert(tweet)
    return close

def decideClosest(bcks, rec):
    if bcks[1] > rec[1]:
        return bcks
    else:
        return rec

tweet     = None
done      = 0
starttime = 0
systime   = datetime.now()

with open(sys.argv[1]) as f:
    for l in f:
        ws        = l.split()
        k         = unicode(ws[0])
        v         = unicode(ws[1])
        oovMap[k] = v

skipped   = 0

processed = 0


print 'start 3'

# start collecting stories in a seperate Thread
t = threading.Thread(target=get_stories.run, args=())
t.start()

print 'start 4'

while True:
    if len(unprocessed_tweet_queue) != 0:
        t     = unprocessed_tweet_queue.popleft()
        # t   = json.loads(l)
        msg   = t['tweet']
        ts    = int(t['timestamp'])
        msgid = int(t['id'])
        uid   = int(t['user']['id'])
        if utils.qualified(msg, TAGS, IGNORE, MIN_TOKENS):
            tweet = Tweet(msg, ts, msgid, uid)
            incr = TfIdf.getVals(tweet, oovMap)
            # print tweet.getVector()
            buckets.updateRndVec(incr)
            closeBuck    = getClosestNeighborBuckets(tweet)
            closeRecent  = getClosestNeighborRecent(tweet, closeBuck[1])
            closeoverall = decideClosest(closeBuck,closeRecent)
            other        = closeoverall[0]
            if other:
                t['nearneigh'] = other.msgid
            else:
                t['nearneigh'] = -1
            t['cossim'] = closeoverall[1]
            processed_tweet_queue.put(t) # add tweet to second queue
            # sys.stdout.write(json.dumps(t) + '\n')
        else:
            print 'skipped'
            skipped += 1


        done += 1
        current = int(ts) / 1000
        if current-starttime > 900:
            aftertime = datetime.now()
            delta     = aftertime-systime
            systime   = aftertime
            dt        = divmod(delta.seconds,60)
            sys.stderr.write(str(done) + ' Tweets done in ' + str(dt[0]) + ' min ' + str(dt[1]) + ' sec.\n')
            starttime = current

        processed += 1
        if processed%100 == 0:
            print '{0} tweets processed'.format(processed)
    # else:
    #     print 'Processor is waiting for tweets'

sys.stderr.write('Processed ' + str(done) + ' tweets in total.\n')
sys.stderr.write('Skipped a total of ' + str(skipped) + ' tweets.\n')
