# My Portfolio!
I thought I'd showcase my work in Python and learn how to use git at the same time. Turns out I have way more code than I thought I did! Here's how it's organized:

# HBNL_tools
Is a work-related folder of modules I've coded to analyze Event-Related Potential (brain wave) data and neuropsychological data.  Each module is for a different data type or project involving PyMongo.
No assembly required.  


# web scraping
For a project with a friend that involved scraping html tables titled "Team Batting" from http://www.baseball-reference.com and searching data frame based on player name and statistic. 
Pandas is your friend.

# tweepy
Is a folder of tools I've coded that use Twitter's [REST API](http://docs.tweepy.org/en/v3.5.0/api.html) to programatically manage a twitter account.  Built-in rate-limit handling.  Stores 
[API response](https://gist.github.com/hrp/900964)into data frame and allows user to manipulate columns to find quality followers (e.g. if a user's account was created 3 years ago and they've
posted 50 tweets since then, they may not be a "quality" follower).  Contains functions to mass unfollow users, follow new users by tweet text/hashtag/location/etc., and post tweets from a text 
file at fixed intervals. Also contains an example of Twitter's Streaming API to collect "live tweets" as they happen.