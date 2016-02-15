from tweet_schema import Tweet
from flask import Flask, render_template, send_from_directory, redirect, url_for
from mongoengine import *
from subprocess import call
import redis
import datetime
from datetime import timedelta

app = Flask(__name__)
app.config['DEBUG'] = True

print 'flask started'

r = redis.StrictRedis(host='localhost', port=6379, db=0)
connect('Tweets')

print 'db connected'

@app.route("/")
def main():
    print 'main entered'
    fetch_count        = int(r.get('fetch_count'))
    tweet_count        = int(r.get('tweet_count'))
    modified_at        = r.get('modified_at')
    target             = 100000
    avg_time_per_fetch = float(r.get('avg_time_per_fetch'))
    
    
    db_tweets_count = Tweet.objects().count()
    tweets_left = (target - fetch_count*100)
    est_breaks = (tweets_left/180)*15*60 # 15 min break after 180 requests
    est_time = ((tweets_left * avg_time_per_fetch) / 100) + est_breaks
    
    if est_time < 0:
        est_time = 0

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
    return send_from_directory('/home/ubuntu', 'tweet_db')

@app.route("/create_dump")
def createDump():
    outfile = '/home/ubuntu/'
    call(["mongodump", "-d","Tweets","-o",outfile],shell=True)
    call(["zip", "-r","/home/ubuntu/zipfile.zip","/home/ubuntu/Tweets"],shell=True)
    return redirect(url_for('main'))

if __name__ == "__main__":
    # connect to DB
    app.run(host='0.0.0.0')
