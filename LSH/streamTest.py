#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

#Variables that contains the user credentials to access Twitter API 
access_token = "835513550-cRrDufNgd93ZUhEbaZ8FCiZQZ1awSg5Ll1Qaau3j"
access_token_secret = "jBoh0jl1W7N32W0FfAbXwuuLDJdmcrR90SGpFJMXv68hS"
consumer_key = "H8x9RBCEGbyTCBqUdVjxzmUDs"
consumer_secret = "kf1R7kgq4zNgzhc3eggkXAxSTIUwPA9a9NoyYtfiS0xWNgSkwr"


#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):

    def on_data(self, data):
        print data
        return True

    def on_error(self, status):
        print status


if __name__ == '__main__':

    #This handles Twitter authetification and the connection to Twitter Streaming API
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)

    #This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
    stream.filter(track=['python', 'javascript', 'ruby'])
