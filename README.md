# My Portfolio!
I thought I'd showcase my work in Python and learn how to use git at the same time. Turns out I have way more code than I thought I did! Here's how it's organized:

# HBNL_tools
A collection of modules I've developed to check the integrity of incoming qualitative and quantiative research data, utilize shell scripts to analyze brain wave data, and visualize data extracted from lab database
Modules used: pandas, bokeh, PyMongo, numpy, subprocess, re, itertools, collections, os, glob...



# web scraping
Project that involved scraping html tables titled "Team Batting" from http://www.baseball-reference.com and creating visualizations from scraped data 
Modules used: BeautifulSoup, requests, pandas, collections, bokeh...

# tweepy
Streaming API: Search twitter for 'live' tweets (i.e. tweets just tweeted) and stores tweet text, location, friends count, etc. into SQL DB.  
REST API: Programatically manage your twitter account
	 1) follow users based on tweet text, location, ratio of friends/followers, etc.
	 2) mass unfollow (i.e. if you follow someone who doesn't follow you back, unfollow them)
	 3) follow new users based on conditions: stores 'important' parts of Twitter JSON response (http://docs.tweepy.org/en/v3.5.0/api.html) in pandas data frame
	    --> iterates over each row and prompts user if they would like to follow this twitter user 
Modules used: tweepy, pandas, sqlite3, json... 


To view plots in notebooks: 

Bokeh uses Dynamic JS & github doesn't yet support it so...
[Go here](http://nbviewer.jupyter.org/) & paste the url of the notebook you want to view
[Example] (http://nbviewer.jupyter.org/github/FelicianoAnthony/Python_projects/blob/master/web-scraping/br_scraping_walkthrough.ipynb)