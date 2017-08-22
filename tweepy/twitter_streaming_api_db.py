#!/usr/bin/env python

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
import json
import sqlite3
from pprint import pprint
import tweepy_keys as config
import time

import sys
sys.path.append('/Users/Anthony/Desktop/python_projects/twitter/')

auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


conn = sqlite3.connect('twitter_one13.db')
c = conn.cursor()


class Tweet():

    # Data on the tweet
    def __init__(self, user_id, lang, location, handle, status_count, followers_count,
                 friends_count, tweet_text, user_creation, retweet_count, tweet_time, 
                 time_zone, utc_offset, coordinates):
        
        
        self.user_id = user_id
        self.lang = lang
        self.location = location
        self.handle = handle
        self.status_count = status_count
        self.followers_count = followers_count
        self.friends_count = friends_count
        self.tweet_text = tweet_text
        self.user_creation = user_creation
        self.retweet_count = retweet_count
        self.tweet_time = tweet_time
        self.time_zone = time_zone
        self.utc_offset = utc_offset
        self.coordinates = coordinates
    
    # Inserting that data into the DB
    def insertTweet(self):
        c.execute("INSERT INTO tweets (user_id, lang, location, handle, status_count, followers_count, friends_count, tweet_text, user_creation, retweet_count, tweet_time, time_zone, utc_offset, coordinates) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
            (self.user_id, self.lang, self.location, self.handle, self.status_count, self.followers_count, self.friends_count, self.tweet_text, self.user_creation, self.retweet_count, self.tweet_time, self.time_zone, self.utc_offset, self.coordinates))
        conn.commit()

# Stream Listener class
class TweetStreamListener(tweepy.StreamListener):
    
    
    def __init__(self):
        self.num_tweets = 0  
        
    # When data is received
    def on_data(self, data):

        # Error handling because teachers say to do this
        try:

            # load as json
            tweet = json.loads(data)
            
            tweet_data = Tweet(tweet['user']['id_str'], 
                               tweet['lang'],
                               tweet['user']['location'], 
                               tweet['user']['screen_name'], #@ handle
                               tweet['user']['statuses_count'],
                               tweet['user']['followers_count'],
                               tweet['user']['friends_count'],
                               str(tweet['text'].encode('utf-8')),
                               tweet['user']['created_at'],
                               tweet['retweet_count'],
                               tweet['created_at'],
                               tweet['user']['time_zone'],
                               tweet['user']['utc_offset'],
                               tweet['coordinates'])
                                   
                tweet_data.insertTweet()
                self.num_tweets+=1
                print('inserted')
        
        # Let me know if something bad happens            
        except Exception as e:
            print(e, '...sleeping...')
            time.sleep(10)
            pass
        
        if self.num_tweets % 100 == 0 :
            time.sleep(5)
            print('sleeping for 5 seconds')
        if self.num_tweets == 2000:
            sys.exit(0)

        return True



sapi = tweepy.streaming.Stream(auth, TweetStreamListener())
sapi.filter(track=['#trump'])