#!/usr/bin/env python
import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_salary_table(player_url):
    
    page = requests.get(player_url).text


    table_code = page[page.find('<table class="sortable stats_table" id="br-salaries"'):]
    soup = BeautifulSoup(table_code, 'lxml')

    table_body  = soup.find('tbody')
    
    #this block is for salary
    salary_lst = []
    for i in table_body.findAll('tr'):
        for j in i.findAll('td'):
            if j['data-stat'] == 'salary':
                sal = j.get_text()
                salary_lst.append(sal)
                
    #this block is for years              
    years = table_body.findAll('th')                          
    years_lst = []
    for i in years:
        ls = i.get_text()
        years_lst.append(ls)
    del years_lst[-1]
        
    df = pd.DataFrame(years_lst)
    df['salary'] = salary_lst
    df1 = df.reset_index()
    df2 = df1.rename(columns={0: 'years'})
    df3 = df2.set_index(keys = ['years'])
    return df3

url = input('Enter a path bitch')

scrape_salary_table(url)