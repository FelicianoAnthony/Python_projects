
# go to https://dev.twitter.com/ and make developer account to get developer keys and access tokens 
# store these as variables in a separate file and import it as a module
import sys
sys.path.append('')

import tweepy_dev_tokens as config 
import pandas as pd
import time
import tweepy
import re
pd.set_option('display.max_colwidth', -1)

auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True,retry_count=6)


def follow_bot(hashtag_or_text, integer):
    """follow integer amount of users by searching #hashtag or plain text"""

    # get tweet text and author metadata 
    tweet_data=[]
    count = 0
    print('Fetching tweets matching', hashtag_or_text)
    for tweet in tweepy.Cursor(api.search, q= hashtag_or_text).items(integer): 
        try:
            count +=1
            if count % 5 == 0:
                time.sleep(2)
                tweet_data.append(tweet)
        except Exception as e:
            print(str(e) + 'Probably rate limited. \n  Waiting 15 minutes.')
            time.sleep(60*15)

    # get a list of ids of people you already follow 
    friends_id = [] 
    fr_count = 0
    print('Fetching friend ids...', '\n\n')
    for friend in tweepy.Cursor(api.friends_ids).items(): 
        try: 
            fr_count +=1
            if fr_count % 5 == 0:
                time.sleep(2)
                friends_id.append(friend)
            else:
                friends_id.append(friend)
        except Exception as e:
            print(str(e) + 'Probably rate limited. \n  Waiting 15 minutes.')
            time.sleep(60*15)
    
    # if you dont already follow authors of new tweet -- follow them 
    follow_count = 0
    for tweet in tweet_data:
        if tweet.author.id not in friends_id:  
            follow_count +=1
            try: 
                api.create_friendship(tweet.author.id)
                time.sleep(6)
                print(str(follow_count) + " Following | @{0}".format(api.get_user(tweet.author.id).screen_name) + '\n'+ 'Tweet Text |' + tweet.text + '\n') 
            except Exception as e:
                print(str(e) + 'Probably rate limited. \n  Waiting 15 minutes.')
                time.sleep(60*15)



def follow_choice(text, integer):
    """Search for users to follow by hashtag or text and 
        displays tweet user metadata as a data frame and
        prompt user to follow or not"""

    # get entire JSON response to make df
    tweet_data=[]
    count = 0
    print('Fetching tweets matching', text)
    for tweet in tweepy.Cursor(api.search, q= text).items(integer): 
        try: 
            count +=1
            if count % 5 == 0:
                time.sleep(2)
                tweet_data.append(tweet)
            else:
                tweet_data.append(tweet)
        except Exception as e:
            print(str(e) + 'Probably rate limited. \n  Waiting 15 minutes.')
            time.sleep(60*15)
            
    author_ids =  [i.author.id_str for i in tweet_data]
    
    # map specific parts of tweet metadata to pandas columns
    first_col = [tweet.author.name for tweet in tweet_data] 
    data_set = pd.DataFrame(first_col, columns = ["PROFILE NAME:"])
    data_set["TWEET TEXT:"] = [tweet.text for tweet in tweet_data]
    data_set["FOLLOWERS COUNT:"] = [tweet.author.followers_count for tweet in tweet_data]
    data_set["FRIENDS COUNT:"] = [tweet.author.friends_count for tweet in tweet_data]
    data_set["# OF TWEETS:"] = [tweet.author.statuses_count for tweet in tweet_data]
    data_set["LOCATION:"] = [tweet.author.location for tweet in tweet_data]    
    data_set["USER CREATED AT:"] = [tweet.author.created_at for tweet in tweet_data]
    
    # potential responses to input
    yes = ['yes','y', 'ye', 'Yes', 'YES'] 
    no = ['no','n', 'No', 'NO']
    close = ['quit', 'exit', 'leave', 'bye', 'q']

    # iterate over df rows and display info prompting user to decide if they want to follow or not 
    for i,j in zip(data_set.index, author_ids):
        try: 
            print('\n\n\n\n', data_set.ix[i], '\n\n\n\n')
            answer = input('\n' + "Follow @{0}? ".format(api.get_user(j).screen_name))
            if answer in yes: 
                time.sleep(6)
                api.create_friendship(j) 
                print('You just followed someone')
            elif answer in no:#2 --> check to see if input in list 
                print('Maybe next time...' + '\n')
            elif answer in close: #3---> exit program 
                sys.exit(0)
            elif re.match('^[a-zA-Z0-9_.-]*$', answer): #4--> regex to get any alphanumeric combinations
                pass
        except tweepy.TweepError:
            print('Sleeping for 15 minutes...')
            time.sleep(60*5)
    return True





def unfollow_bot(integer):
    '''**this is a bot that will unfollow all the users who dont follow you back
       **integer= the number of users you want to unfollow'''
    
    #store followers in a list
    followers_ids = []
    fo_count = 0
    print('Fetching followers ids...', '\n\n')
    for follower in tweepy.Cursor(api.followers_ids).items():
        try: 
            fo_count +=1
            if fo_count % 5 == 0:
                time.sleep(2)
                followers_ids.append(follower)
            else:
                followers_ids.append(follower)
        except Exception as e:
            print(str(e) + 'Probably rate limited. \n  Waiting 15 minutes.')
            time.sleep(60*15)
        
    # get a list of people you already follow 
    friends_ids = [] 
    fr_count = 0
    print('Fetching friend ids...', '\n\n')
    for friend in tweepy.Cursor(api.friends_ids).items(): 
        try: 
            fr_count +=1
            if fr_count % 5 == 0:
                time.sleep(2)
                friends_ids.append(friend)
            else:
                friends_ids.append(friend)
        except Exception as e:
            print(str(e) + 'Probably rate limited. \n  Waiting 15 minutes.')
            time.sleep(60*15)
        
    #if someone you follow isn't following you, unfollow them   
    unfollow_count = 0
    for i in friends_ids:
        if i not in followers_ids:
            try:
                unfollow_count +=1
                print (str(unfollow_count) + " Unfollowing @{0}".format(api.get_user(i).screen_name))
                api.destroy_friendship(i)
                time.sleep(6)
                if unfollow_count == int(integer):
                    print('Exiting program...')
                    sys.exit(0)
            except Exception as e:
                print(str(e) + 'Probably rate limited. \n  Waiting 15 minutes.')
                time.sleep(60*15)