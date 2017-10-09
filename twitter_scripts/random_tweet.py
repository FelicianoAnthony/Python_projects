from collections import OrderedDict
from bs4 import BeautifulSoup
from random import choice
from time import sleep
import urllib.request
import sqlite3
import tweepy
import praw
import sys
import os
sys.path.append('/path_to/api_keys/and/subreddit_list')

import twitter_keys as tk
import reddit_keys as rk

def reddit_login(reddit_api_keys):
    """reddit API login info """
    login = praw.Reddit(user_name =reddit_api_keys[0],
                        password = reddit_api_keys[1], 
                        client_id = reddit_api_keys[2],
                        client_secret = reddit_api_keys[3],
                        user_agent = 'reddit twitter thing thing v1')
    return login

def tweepy_login(tweepy_api_keys):
    """ tweepy API login info """

    auth = tweepy.OAuthHandler(tweepy_api_keys[0], tweepy_api_keys[1])
    auth.set_access_token(tweepy_api_keys[2], tweepy_api_keys[3])
    return tweepy.API(auth, wait_on_rate_limit=5)

def read_subreddit_file(path):
    """ path to file with subreddits """

    subreddits = []
    with open(path, 'r') as file:
        for l in file:
            sub = l.replace('\n', '')
            subreddits.append(sub)
    return subreddits    

def create_db_table(full_path_to_db):
    """ create new DB """
    if os.path.exists(full_path_to_db):
        print(full_path_to_db + ' already exists')
    else:
        conn = sqlite3.connect(full_path_to_db)
        c = conn.cursor()
        c.execute("""CREATE TABLE reddit_posts_to_twitter
            (article_url text, 
            article_title text)""")
        conn.commit()
        conn.close()
        print('Created new database in ' + full_path_to_db)
    
def get_random_subreddit_top_posts(reddit_api_keys, random_subreddit):
    """ returns highest upvoted post in rising posts """
    
    r_login = reddit_login(reddit_api_keys)
    
    page = r_login.subreddit(random_subreddit)
    top_posts = page.hot(limit=100)
    print('this is', page, '\n\n')

    try:
        posts_dict = {}
        for post in top_posts:
            if post.ups > 1000:
                value = post.ups, post.url
                posts_dict[post.title] = value

        # sort by most upvotes & get first entry         
        sorted_by_upvotes = OrderedDict(sorted(posts_dict.items(),key=lambda x:x[0], reverse=True))
        keys = list(sorted_by_upvotes)
        value = sorted_by_upvotes[keys[0]]
        post_dict = {}
        post_dict[keys[0]] = value
        return post_dict
    except Exception as e:
        print(str(e), "||" , random_subreddit,"||", "isn't a subreddit. Check your subreddits text file")
        sys.exit(0)

def post_tweet(tweepy_keys, tweet_dict, tweet_frequency, db_path):
    """takes reddit post dict of tuples, write to DB if not there & posts to twitter"""

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    for k,v in tweet_dict.items():
        try:
            c.execute('SELECT * FROM reddit_posts_to_twitter WHERE (article_url=? AND article_title=?)', (k, v[1]))
            entry = c.fetchone()

            if entry is None:
                c = conn.cursor()
                c.execute("""
                    INSERT INTO 
                        reddit_posts_to_twitter 
                    VALUES
                        (?, ?)
                """, (k, v[1]))
                conn.commit()
                tweet = k + '\n'+ v[1]
                api = tweepy_login(tweepy_keys)
                api.update_status(tweet)
                sleep(int(tweet_frequency))
                print ('\n', 'New entry added', '\n', k, v[1], '\n')
            else:
                print ('Entry found')
        except Exception as e:
            print(str(e), 'Probably character limit')
            
def reddit_tweeter(tweepy_api_keys, reddit_api_keys, db_path, 
	               int_tweets_to_tweet, tweet_frequency, subreddit_lst_path):
    """ posts tweet from random subreddit that has highly voted post"""
    
    r_login = reddit_login(reddit_api_keys)
    count=0
    while count < int(int_tweets_to_tweet):
        count+=1
        subreddit_list = read_subreddit_file(subreddit_lst_path)
        random_subreddit = choice(subreddit_list)
        print('Checking DB for duplicates...')
        posts_dict = get_random_subreddit_top_posts(reddit_api_keys, random_subreddit)
        print(count, post_tweet(tweepy_api_keys, posts_dict, tweet_frequency, db_path))
        
 # user prompts      
msg = input('Make sure you append the path to your praw & reddit API credentials at the top of this file.\nPress enter to continue. ')
db_path = input('Enter your database path ending with .sqlite > ')
db_new = input('Is this a new database? y/n > ')
if db_new in ['y','Y', 'Yes','yes']:
	create_db_table(db_path)
subreddit_list = input('Enter the path to your subreddit list ending with txt.\nEach subreddit should be on a separate line. > ')
num_tweets = input('Enter number of tweets you want to send  > ')
freq_tweets = input('Enter amount of time to wait between each tweet in seconds.\n About 1 tweet/5 seconds is max. > ')

tweepy_api_keys = tk.CONSUMER_KEY, tk.CONSUMER_SECRET, tk.ACCESS_TOKEN, tk.ACCESS_TOKEN_SECRET
reddit_api_keys = rk.username, rk.password, rk.client_id, rk.client_secret

reddit_tweeter(tweepy_api_keys, reddit_api_keys, db_path, num_tweets, freq_tweets, subreddit_list)

input('Press enter to close. > ')