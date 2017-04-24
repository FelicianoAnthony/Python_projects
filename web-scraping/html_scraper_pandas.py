#!/usr/bin/env python
from collections import OrderedDict
from bs4 import BeautifulSoup
import urllib.request
import pandas as pd
import re
import sys

def html_table_scraper(br_url, player, stat):
    '''Arguments: br_url = baseball-reference.com url to "Team Batting" table for any season
                   player = name of player to be looked up
                   stat = type of statistic to look up (all uppercase letters)'''
    
    #read html as data frame
    df = pd.read_html(br_url, flavor='html5lib', attrs={'class': 'sortable'})
    
    batting_df = df[0]
    pitching_df = df[1]
    
    #do a little formatting 
    bat_to_drop =  [col for col in batting_df.columns if col.startswith('Unnamed')]
    batting_df1 = batting_df.drop(bat_to_drop,1)
    
    #removes anything between paranthesis & unwanted characters
    batting_df1['Name'] = batting_df1['Name'].str.replace(r'\(([^()]+)\)', '')
    batting_df1['Name'] = batting_df1['Name'].str.replace('*', '')
    batting_df1['Name'] = batting_df1['Name'].str.replace('#', '')
    
    #set index
    batting_df2 = batting_df1.set_index(keys='Name')
    
    while True:
        try:
            batting_df3 = batting_df2.loc[player][stat]
            d={'Name': player, stat: batting_df3}
            return d
        except KeyError as e:
            print('Error:', e, 'Check spelling')
            sys.exit(0)
        else: 
            break