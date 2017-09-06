#!/usr/bin/env python3
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from bs4 import BeautifulSoup
from math import ceil 
import urllib.request
import requests
import sqlite3
import time
import sys
import os
import re


def setup_webdriver(path_to_driver): 
    '''set up webdriver'''

    chromedriver = path_to_driver
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)
    return driver


def create_soup(url):
    ''' create bs4 object '''
    
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36"})
    
    return BeautifulSoup(r.content, "html5lib")


def scrape_job_post_links(url):
    ''' returns all links from a query on indeed mobile '''
    
    # create soup
    soup = create_soup(url)

    # get all job links
    indeed_baseurl = 'https://www.indeed.com/m/'
    h2_tags = soup.find_all('h2', {'class':'jobTitle'})
    job_links = [indeed_baseurl + a['href'] for h in h2_tags for a in h.find_all('a')]
    return job_links

def indeed_webdriver_crawler(job_name, job_location, int_pages_to_search,
                             path_to_driver):
    ''' query indeed mobile & to get all job links from set number of pages.
        returns all scraped links'''
    
    # init webdriver
    driver = setup_webdriver(path_to_driver)

    # query indeed
    driver.get("https://www.indeed.com/m")
    driver.find_element_by_name('q').clear()
    driver.find_element_by_name('q').send_keys(job_name)
    driver.find_element_by_name('l').clear()
    driver.find_element_by_name('l').send_keys(job_location)
    driver.find_element_by_xpath('/html/body/form/p[3]/input').click()
    
    # start scraping with most recent posts 
    driver.get(driver.current_url + '&sort=date')
    
    # set list
    job_links = []

    # unique way to identify first page--- did because of xpath
    #if driver.current_url.split('=')[2][-5:] != 'start':
    if len(driver.current_url.split('=')) > 2:
        # get job links from 1st page only 
        first_scrape = scrape_job_post_links(driver.current_url)
        job_links.extend(first_scrape)
        print('yes1')

        # this is xpath for NEXT button for only first page
        driver.find_element_by_xpath('/html/body/p[22]/a').click()
        print('yes2')

    # scrape all job links for x amount of pages 
    c=0
    for x in range(int(int_pages_to_search)):
        c+=1
        # get oldest job posting date on the page
        soup = create_soup(driver.current_url)
        last_date = [i.get_text() for i in soup.find_all('span', {'class': 'date'})][-1]
        print('Last date on page', c, 'of', int_pages_to_search, '==>', last_date)
        
        # scrape links, add to list, next page
        page_urls = scrape_job_post_links(driver.current_url)
        job_links.extend(page_urls)
        time.sleep(2)
        driver.find_element_by_xpath('/html/body/p[22]/a[2]').click()
    
    # return only unique links 
    no_dupes = list(set(job_links))
    return no_dupes

def view_jobs(driver, jobs_filtered, sleep_time,
              path_to_driver):
    ''' given a list of urls, 
        load each url for given amount of time'''

    driver = setup_webdriver(path_to_driver)

    for j in jobs_filtered:
        concat_url = 'window.open("' + i + '","_blank");'
        driver.execute_script(concat_url)
        time.sleep(int(sleep_time))


def create_db_table(full_path_to_db):

    conn = sqlite3.connect(full_path_to_db)
    c = conn.cursor()
    c.execute('''CREATE TABLE indeed_jobs
        (id integer primary key, data,
        url text, 
        company_name text, 
        job_title text)''')

    conn.commit()
    conn.close()

def post_to_db(jobs_filt, full_path_to_db, sleep_int, 
               path_to_driver, create_db=None):
    ''' given a list of indeed mobile urls, 
        checks to see if url in DB & if not...
        writes to DB and displays new tab in same window for n amount of time...'''
    
    # init webdriver
    driver = setup_webdriver(path_to_driver)

    # if new db reating DB 
    if create_db:
        create_db_table(full_path_to_db)
    
    # set up connection BEFORE loop 
    conn = sqlite3.connect(full_path_to_db)
    c = conn.cursor()

    print('Checking DB for duplicates...')
    new_urls = []
    for url in jobs_filt:
        driver.get(url)
        soup = create_soup(url)
        
        # get additional unique identifiers to post to DB 
        job_uid = driver.find_element_by_xpath('/html/body/p[1]').text
        job_title = job_uid.split('\n')[0]
        job_company = job_uid.split('\n')[1]

        # make sure post doesnt already exist in DB
        c.execute('SELECT * FROM indeed_jobs WHERE (url=? AND company_name=? AND job_title=?)', (driver.current_url, job_company, job_title))
        entry = c.fetchone()

        if entry is None:
            # add to DB if not found 
            c.execute("insert or ignore into indeed_jobs (url, company_name, job_title) values (?, ?, ?)",
                (driver.current_url, job_company, job_title))
            conn.commit()
            
            # show that window for x amount of time
            print ('\n\n', 'New entry added', '\n', job_title, job_company, '\n\n')
            new_urls.append(url)
        else:
            print ('Entry found')

    len_urls = len(new_urls)
    msg = '{} {} {} {} {}'.format('There are',  len_urls,  
                                  'urls and this is gonna take', len_urls * sleep_int / 60, 
                                  'minutes to view. Break it up into chunks by entering number. Enter n to skip')
    ques = input(msg)
    if ques == 'n':
        for u in new_urls:
            concat_url = 'window.open("' + u + '","_blank");'
            driver.execute_script(concat_url)
            time.sleep(int(sleep_int))
    else:
        lens = len(new_urls)

        iters = lens / int(ques)
        
        iters_r = ceil(iters)
        # should really be a while Looop!!!!!!!!!!!!!
        count = 0
        for x in range(iters_r):
            for u in new_urls:
                count+=1
                concat_url = 'window.open("' + u + '","_blank");'
                driver.execute_script(concat_url)
                time.sleep(int(sleep_int))
                tst.append(u)
                if count % int(ques) ==0:
                    q = input('Press enter to continue')
                if count == lens:
                    sys.exit(1)

def query_job_posting(url, query_list=False, query_phrase_as_str=False): 
    ''' |QUERIES MUST BE LOWERCASE|
        query_list = turns job post to list of words & if any word in list match, return url 
        query_phrase_as_str = search job post as 1 big list for phrases '''
    
    # create url and find job description div 
    soup = create_soup(url)
    desc = soup.find_all('div', {'id': 'desc'})
    
    # get text and flatten list
    desc_lol = [i.get_text().lower().split() for i in desc]
    desc_flattened = [inner for outer in desc_lol for inner in outer]
    
    # query for 'phrases' in job posting (e.g. 'fixed income')
    if query_phrase_as_str:
        no_split= [i.get_text().lower() for i in desc]
        regex =  [(re.sub(r'[^\w\s]',' ', i)) for i in no_split]
        equal_spaceing = [i.replace('  ', ' ') for i in regex ]
        return [url for i in equal_spaceing if query_phrase_as_str in i]

    # remove all funny characters & empty strings 
    desc_regex = [(re.sub('[^A-Za-z0-9]+', '', i)) for i in desc_flattened]
    desc_query = [i for i in desc_regex if i]
    
    
    # if any word matches, return link -- more effective 
    if query_list:
        for i in desc_query:
            if any(word in i for word in query_list):
                return url


def combined_all(job_title, job_company, pages_to_scrape,
                 db_path, sleep_int, path_to_driver, first_run=None,
                 query_list=None, query_phrase_as_str=None): 
    ''' fewest number of arguments to do everything above in 1 function '''

    jobs_lst = indeed_webdriver_crawler(job_title, job_company, pages_to_scrape, path_to_driver)
    
    if query_list or query_phrase_as_str:
        matches =  [query_job_posting(i, query_list=query_list, query_phrase_as_str=query_phrase_as_str) for i in jobs_lst]
        return post_to_db(matches, db_path, sleep_int, path_to_driver, create_db=first_run)

    return post_to_db(jobs_lst, db_path, sleep_int, path_to_driver, create_db=first_run)
