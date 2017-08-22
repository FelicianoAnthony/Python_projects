# My Portfolio!
I thought I'd showcase my work in Python and learn how to use git at the same time. Turns out I have way more code than I thought I did! Here's how it's organized:

# HBNL_tools
A collection of modules I've developed while working at the Henri Begleiter Neurodynamics Laboratory in Brooklyn.  These modules check the integrity of incoming qualitative and quantitative research data, utilize shell scripts to analyze brain wave data, visualize data extracted from lab database, and much more.

### Packages used: pandas, bokeh, PyMongo, numpy, subprocess, re, itertools, collections, os, glob...



# Web scraping
Project that involved building a web scraper to download MLB statistics from the [”Team Batting tables”](https://www.baseball-reference.com/teams/NYM/2017.shtml) for any combination of teams and seasons and creating visualizations from scraped data 

### Packages used: BeautifulSoup, requests, pandas, collections, bokeh...

# Twitter Tools
**Streaming API**: Search twitter for 'live' tweets (i.e. tweets just tweeted) and stores tweet text, location, friends count, etc. into SQL DB.  
**REST API**: Programatically manage your twitter account...

	     1) follow users based on tweet text, location, ratio of friends/followers, etc.
	     
	     2) mass unfollow (i.e. if you follow someone who doesn't follow you back, unfollow them)
	     


### Packages used: tweepy, pandas, sqlite3, json... 


# To view plots in notebooks: 

Bokeh uses Dynamic JS & github doesn't yet support it so...
[go here](http://nbviewer.jupyter.org/) & paste the url of the notebook you want to view

[Example](http://nbviewer.jupyter.org/github/FelicianoAnthony/Python_projects/blob/master/HBNL_tools/bokeh_notebooks/sessions_plots.ipynb)