#!/usr/bin/env python
import pika
import time
import json
import numpy as np
from sklearn import metrics
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import cPickle
import os
import utils

connection        = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel           = connection.channel()
project_root      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_dump_path   = os.path.join(project_root, 'Classifier Models', 'Naive Bayes')
count_vect        = None
tfidf_transformer = None
clf               = None

# declare all queues
channel.queue_declare(queue='FYP.Q.Filter.TweetMessage', durable=True)
channel.queue_declare(queue='FYP.Q.Cluster.NewsTweetMessage', durable=True)
channel.queue_declare(queue='FYP.Q.Generic.NonNewsTweetMessage', durable=True)

print('[*] Waiting for messages. To exit press CTRL+C')

# initialize models here(saved to disk already)
models = [['count_vect.60_40.0.886620715777.plk', 'tfidf_transformer.60_40.0.886620715777.plk', 'clf.60_40.0.886620715777.plk']]

def loadModels():
    
    global count_vect, tfidf_transformer, clf

    print "filter: Loading Models ..."
    with open(os.path.join(model_dump_path, models[0][0]), "rb") as fid:
        count_vect = cPickle.load(fid)

    with open(os.path.join(model_dump_path, models[0][1]), "rb") as fid:
        tfidf_transformer = cPickle.load(fid)

    with open(os.path.join(model_dump_path, models[0][2]), "rb") as fid:
        clf = cPickle.load(fid)
    print "filter: Models loaded!"
    
    
def callback(ch, method, properties, body):
    body = json.loads(body)
    print(" [x] Received %r" % body['tweet'])
    X_new_counts = count_vect.transform([utils.cleanThis(body['tweet'])])
    X_new_tfidf = tfidf_transformer.transform(X_new_counts)
    predicted = clf.predict(X_new_tfidf)
    print predicted

    # acknowledge the sender (streamer)
    ch.basic_ack(delivery_tag = method.delivery_tag)


if __name__ == '__main__':
    loadModels()
    channel.basic_qos(prefetch_count=10)
    channel.basic_consume(callback,queue='FYP.Q.Filter.TweetMessage')
    channel.start_consuming()

