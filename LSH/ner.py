import nltk
import re
import time
import pprint
import urllib
from pymongo import MongoClient

client = MongoClient()
db = client.shuffled_DB2

# This is to get the type of a tuple
tup = (1, 2, 3)

# Types of named entities that can be recognized from the tweet
entities = ["ORGANIZATION", "PERSON", "LOCATION", "DATE", "TIME", "MONEY", "PERCENT", "FACILITY", "GPE"]

def checkForNamedEntities(tree):
  # This means the node is a tuple
  if(type(tree) == type(tup)):
    return False
  else:
    tag = tree.label()
    if(tag in entities):
      return True  
    else:
      found = False
      for node in tree:
        if(checkForNamedEntities(node)):
          found = True
          return True
            



def checkNER(tweetsList):
  for tweet in tweetsList:
    # Tokenize the words in the given tweet
    tokenized = nltk.word_tokenize(tweet)

    # Identify the parts of speech of each token
    tagged = nltk.pos_tag(tokenized)

    #Identify named entites using the parts of speech from the Tweet
    tree = nltk.ne_chunk(tagged)
    if(checkForNamedEntities(tree)):
      return True
    else:
      return False
    