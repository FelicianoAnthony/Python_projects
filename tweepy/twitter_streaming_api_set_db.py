#!/usr/bin/env python
import sqlite3

conn = sqlite3.connect('twitter_one13.db')
c = conn.cursor()
c.execute('''CREATE TABLE tweets
    (user_id integer, 
    lang text, 
    location text, 
    handle text, 
    status_count integer,
    followers_count integer,
    friends_count integer,
    tweet_text text,
    user_creation text,
    retweet_count integer,
    tweet_time integer,
    time_zone text,
    utc_offset integer,
    coordinates integer)''')
conn.commit()
conn.close()