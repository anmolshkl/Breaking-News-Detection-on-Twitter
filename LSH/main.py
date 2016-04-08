from tweet import Tweet
from tfidf import TfIdf
from recenttweets import RecentTweets
from buckets import Bucket, BucketsDB
from datetime import datetime
from operator import itemgetter
import sys, json, utils, math
import get_stories
import pika


print 'start 1'

L             = 36
K             = 13
QUEUE_SIZE    = 20
RECENT_TWEETS = 2000
MIN_TOKENS    = 2

# tweets consisting of these words would be ignored
IGNORE = ['i', 'im', 'me', 'mine', 'you', 'yours']

# tweets consisting these words would be picked --deprecated
TAGS   = ['#news','#breakingnews']

buckets = BucketsDB(L, K, QUEUE_SIZE)
recent  = RecentTweets(RECENT_TWEETS)

# declare incoming channels, queues, exchanes for rabbitmq
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel    = connection.channel()
channel.exchange_declare(exchange='tweets', type='direct')
result     = channel.queue_declare(queue='FYP.Q.Cluster.NewsTweetMessage', durable=True)
queue_name = result.method.queue
channel.queue_bind(exchange='tweets', queue=queue_name, routing_key='news')

# declare outgoing queue
channel.queue_declare(queue='FYP.Q.Grouper.ClusteredTweetMessage', durable=True)

print(' [*] Waiting for Tweets. To exit press CTRL+C')


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

tweet_obj = None
done      = 0
starttime = 0
systime   = datetime.now()
skipped   = 0
processed = 0


def callback(ch, method, properties, body):
    global tweet_obj, done, starttime, skipped, processed, systime

    json_tweet     = json.loads(body)
    sanitized_text = json_tweet['tweet']
    
    msg       = sanitized_text
    ts        = int(json_tweet['timestamp'])
    msgid     = int(json_tweet['id'])
    uid       = int(json_tweet['user']['id'])
    tweet_obj = Tweet(msg, ts, msgid, uid)
    if utils.qualified(tweet_obj, TAGS, IGNORE, MIN_TOKENS):
        incr = TfIdf.getVals(tweet_obj)
        # print tweet.getVector()
        buckets.updateRndVec(incr)
        closeBuck    = getClosestNeighborBuckets(tweet_obj)
        if closeBuck[0] is not None:
            print "CLOSE BUCK: {0}, {1}".format(closeBuck[0].msg, closeBuck[1])
        closeRecent  = getClosestNeighborRecent(tweet_obj, closeBuck[1])
        closeoverall = decideClosest(closeBuck,closeRecent)
        other        = closeoverall[0]
        if other:
            json_tweet['nearneigh'] = other.msgid
        else:
            json_tweet['nearneigh'] = -1
        json_tweet['cossim'] = closeoverall[1]
        channel.basic_publish(exchange='',
                      routing_key='FYP.Q.Grouper.ClusteredTweetMessage',
                      body=json.dumps(json_tweet),
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
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

if __name__ == '__main__':
    channel.basic_consume(callback, queue=queue_name, no_ack=True)
    channel.start_consuming()        

sys.stderr.write('Processed ' + str(done) + ' tweets in total.\n')
sys.stderr.write('Skipped a total of ' + str(skipped) + ' tweets.\n')
