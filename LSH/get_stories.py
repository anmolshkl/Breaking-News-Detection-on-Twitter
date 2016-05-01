import sys, json, entr, time, Queue
import pika

'''
This is the clustering script of the program. It reads each tweet from 
FYP.Q.GetStories.ClusteredTweetMessage, then decodes the JSON they arrive
in into a Python dictionary repre-sentation. After this it creates a new story
with the tweet as the first post if the cosine similarity between the tweet 
and its nearest neighbor is less than MIN COSSIM FOR EXISTING. If it is not, 
it is inserted into the same story as its nearest neighbor. After this, if the 
delta between the timestamp of the tweet being processed and the variable starttime 
is more than WINDOW SIZE IN SECONDS seconds, the current stories are fed into next queue,
before updating start-time with the timestamp of the current tweet.
'''

connection        = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel           = connection.channel()

# ProjectName.Q.<Environment>.<ConsumerName>.MessageTypeName
channel.queue_declare(queue='FYP.Q.GetStories.ClusteredTweetMessage', durable=True)

MIN_UNIQUES              = 8
MIN_ENTROPY              = 3.5
MAX_EMPTY_RUNS           = 3
MIN_TWEETS_IN_SLICE      = 1
MIN_COSSIM_FOR_EXISTING  = 0.5
# WINDOW_SIZE_IN_SECONDS = 900
WINDOW_SIZE_IN_SECONDS   = 60
MAX_TWEETS_IN_WINDOW     = 2000

stories      = {}   # a map of all stories with stories ID (tweet ID) as key
storyMap     = {}   #
storiesUsers = {}   # a mapy of "Tweet ID: unique ID of users who have tweeted a tweet"

n = 0

processed_tweet_queue = Queue.Queue()

def createNew(story):
    storiesUsers[story['id']] = set([story['user']['id']])
    news = {}
    ent  = 0
    # no entities detected yet
    if 'entities' in story:
        ent = len(story['entities'])
    s                     = (story['id'], story['tweet'], ent)
    news['first']         = s
    news['tweets']        = [s]
    news['thisslice']     = 1
    news['total']         = 1
    news['unique']        = 1
    news['runs-with-0']   = 0
    stories[story['id']]  = news
    storyMap[story['id']] = story['id']

def replaceStory(story, stid):
    print "Entered replace story"
    storiesUsers[stid] = set([story['user']['id']])
    news = {}
    ent = 0
    if 'entities' in story:
        ent = len(story['entities'])
    s                     = (story['id'], story['tweet'], ent)
    news['first']         = s
    news['tweets']        = [s]
    news['thisslice']     = 1
    news['total']         = 1
    news['unique']        = 1
    news['runs-with-0']   = 0
    stories[stid]         = news
    storyMap[story['id']] = stid

def insertToExisting(story):
    stid = storyMap[story['nearneigh']]
    if stories[stid]:
        uniq = storiesUsers[stid]
        uniq.add(story['user']['id'])
        q    = stories[stid]
        ent  = 0
        if 'entities' in story:
            ent = len(story['entities'])
        s = (story['id'], story['tweet'], story['sanitized_text'] ent)
        q['tweets'].append(s)
        q['total']            += 1
        q['thisslice']        += 1
        q['unique']           = len(uniq)
        stories[stid]         = q
        storyMap[story['id']] = stid
    else:
        replaceStory(story, stid)

def dump(starttime, current, fid):
    d = {}
    d['data'] = {}
    for k,v in stories.iteritems():
        if v != None:
            if v['thisslice'] < MIN_TWEETS_IN_SLICE:
                v['runs-with-0'] += 1
            else:
                v['runs-with-0'] = 0
                if entr.getEntropy(v) >= MIN_ENTROPY and v['unique'] >= MIN_UNIQUES:
                    d['data'][k] = v
    
    d['start'] = starttime
    d['end'] = current
    if len(d['data']) > 0:
        fid.write(json.dumps(d) + '\n')

    for k,v in stories.iteritems():
        if v != None:
            v['thisslice'] = 0
            v['tweets'] = []
            if v['runs-with-0'] >= MAX_EMPTY_RUNS:
                stories[k] = None


def callback(ch, method, properties, body):
    global n
    current    = 0
    starttime  = 0
    json_tweet = json.loads(body)
    
    if json_tweet['cossim'] >= MIN_COSSIM_FOR_EXISTING:
        insertToExisting(json_tweet)
    else:
        createNew(json_tweet)

    current = int(json_tweet['timestamp']) / 1000
    n += 1
    
    if n >= MAX_TWEETS_IN_WINDOW:
        with open('file.txt', 'w') as fid:
            dump(starttime, current, fid)
            sys.stderr.write('Tweets done: ' + str(n) + '\n')
            starttime = current
            n = n - MAX_TWEETS_IN_WINDOW
    # acknowledge the sender (streamer)
    ch.basic_ack(delivery_tag = method.delivery_tag)


if __name__ == '__main__':
    channel.basic_qos(prefetch_count=10)
    channel.basic_consume(callback,queue='FYP.Q.GetStories.ClusteredTweetMessage')
    channel.start_consuming()
