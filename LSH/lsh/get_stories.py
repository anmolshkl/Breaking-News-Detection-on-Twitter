import sys, json, entr, time, Queue
import global_vars

MIN_UNIQUES              = 2
MIN_ENTROPY              = 3.5
MAX_EMPTY_RUNS           = 3
MIN_TWEETS_IN_SLICE      = 1
MIN_COSSIM_FOR_EXISTING  = 0.5
# WINDOW_SIZE_IN_SECONDS = 900
WINDOW_SIZE_IN_SECONDS   = 60


stories      = {}
storyMap     = {}
storiesUsers = {}

def createNew(story):
    storiesUsers[story['id']] = set([story['user']['id']])
    news = {}
    ent  = 0
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
        s                     = (story['id'], story['tweet'], ent)
        q['tweets'].append(s)
        q['total']            += 1
        q['thisslice']        += 1
        q['unique']           = len(uniq)
        stories[stid]         = q
        storyMap[story['id']] = stid
    else:
        replaceStory(story, stid)

def dump(starttime, current):
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
            sys.stdout.write(json.dumps(d) + '\n')

        for k,v in stories.iteritems():
            if v != None:
                v['thisslice'] = 0
                v['tweets'] = []
                if v['runs-with-0'] >= MAX_EMPTY_RUNS:
                    stories[k] = None

# Set starttime to a high value to process entire input as one story
# Setting to 0 will trigger output on first tweet, thereafter working normally

def run():
    print "getting stories"
    queue = global_vars.processed_tweet_queue
    starttime = 0
    current = 0
    n = 0
    while True:
        if not queue.empty():
            # t = json.loads(l)
            t = queue.get()
            if t['cossim'] >= MIN_COSSIM_FOR_EXISTING:
                insertToExisting(t)
            else:
                createNew(t)

            current = int(t['timestamp']) / 1000
            n += 1
            if current - starttime > WINDOW_SIZE_IN_SECONDS:
                dump(starttime, current)
                sys.stderr.write('Tweets done: ' + str(n) + '\n')
                starttime = current
        else:
            print 'processed_tweet_queue empty.Going to sleep'
            time.sleep(2)

    dump(starttime, current)
    sys.stderr.write('Total number of stories: ' + str(len(stories)) + '\n')
    sys.stderr.write('Total number of tweets: ' + str(n) + '\n')

def s:
    