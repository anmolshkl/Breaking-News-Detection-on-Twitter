from tweet_schema import Tweet
from flask import Flask, render_template, send_from_directory
from mongoengine import *
from subprocess import call
import redis
import datetime
from datetime import timedelta

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['MONGODB_SETTINGS'] = {'db':'Tweets', 'alias':'default'}

r = redis.StrictRedis(host='localhost', port=6379, db=0)

@app.route("/")
def main():
    fetch_count        = int(r.get('fetch_count'))
    tweet_count        = int(r.get('tweet_count'))
    modified_at        = r.get('modified_at')
    target             = 1000000
    avg_time_per_fetch = float(r.get('avg_time_per_fetch'))
    
    
    db_tweets_count = len(Tweet.objects)
    tweets_left = (target - fetch_count*100)
    est_breaks = (tweets_left/180)*15*60 # 15 min break after 180 requests
    est_time = ((tweets_left * avg_time_per_fetch) / 100) + est_breaks
    


    return render_template(
        'index.html',
        db_tweets_count    = db_tweets_count,
        tweet_count        = tweet_count,
        avg_time_per_fetch = avg_time_per_fetch,
        fetch_count        = fetch_count,
        est_time           = str(datetime.timedelta(seconds=int(est_time))),
        modified_at        = modified_at,
        target             = "{:,}".format(target)
    )

@app.route("/download")
def downloadDB():
    return 'Currently Not Working'
    # root_dir = os.path.dirname(os.getcwd())
    # outfile = os.path.join(root_dir, os.pardir, 'static', os.pardir, 'tweet_db')
    # call(["mongodump", "-d","Tweets","-o",outfile],shell=True)
    # return send_from_directory(os.path.join(root_dir,'static'), 'tweet_db')

if __name__ == "__main__":
    # connect to DB
    connect('Tweets')
    app.run(host='0.0.0.0')
