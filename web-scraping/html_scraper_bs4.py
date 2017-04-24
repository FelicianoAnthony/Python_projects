#!/usr/bin/env python
from collections import OrderedDict
from bs4 import BeautifulSoup
import urllib.request
import pandas as pd
import re

class html_table_scraper:
    '''Given a baseball-reference.com url -- scrapes "TEAM BATTING" html table for any season/team into a pandas data frame.
        Allows user to search pandas data frame for a specific player and statistic'''
    
    def scrape_br_html_table(self,url):
        '''Scrapes "TEAM BATTING" html table into pandas data frame'''
        self.url = url

        #create bs object
        r = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(r)

        #find table, find header, find rows
        table = soup.find('div', attrs={'class': 'overthrow table_container'})
        table_head = table.find('thead')
        table_body = table.find('tbody')

        #create table header list
        header = []    
        for th in table_head.findAll('th'):
            key = th.get_text()
            header.append(key)

        #find number of 'empty' rows
        endrows = 0
        for tr in table.findAll('tr'):
            if tr.findAll('th')[0].get_text() in (''):
                endrows += 1

        #find number of rows in table
        rows = len(table.findAll('tr'))
        rows -= endrows + 1  

        #create lists of row data, create ordered dictionary from header and row data...
        #...create list of dictionaries for data frame
        list_of_dicts = []
        for row in range(rows):
            the_row = []
            try:
                table_row = table.findAll('tr')[row]
                for tr in table_row:
                    value = tr.get_text()
                    the_row.append(value)
                od = OrderedDict(zip(header,the_row))
                list_of_dicts.append(od)
            except AttributeError:
                continue 

        #create df
        df = pd.DataFrame(list_of_dicts)

        #change column names to all uppercase for easy searching 
        df.columns = [col.upper() for col in df.columns]

        #strip all bad characters from NAME column to allow searching by name
        df['NAME'] = df['NAME'].str.replace(r'\(([^()]+)\)', '')
        df['NAME'] = df['NAME'].str.replace('*', '')
        df['NAME'] = df['NAME'].str.replace('#', '')

        #set index so it's easier to search
        df1 = df.set_index(keys='NAME')
        return df1

    def search_table(self,url):
        '''given a scraped baseball_reference html table -- searches table for name and statistic of a specific player.
            error handling prompts user to re-enter data if not found in data frame'''
        self.url = url

        df2= self.scrape_br_html_table(url)
        while True:
            try:
                #prompt user for input
                player = input('Enter a player Name:')
                stat = input('Enter a Statistic:') #MUST BE ALL UPPERCASE LETTERS
                #search df
                df3 = df2.loc[player][stat]
                #format output
                d={'Name': player, stat: df3}
                return d
            except KeyError as e:
                print('Error:', e, 'Check spelling')

                pass
            else: 
                break 
table_scraper = html_table_scraper() #instantiate class    