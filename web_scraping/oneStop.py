from selenium.webdriver.common.keys import Keys
from selenium import webdriver 
from bs4 import BeautifulSoup
from collections import defaultdict
import urllib.request
import requests
import sqlite3
import json
import os
import sys
import time
import numpy as np
from PIL import Image

def setup_webdriver(path_to_driver): 
    """set up webdriver"""
    chromedriver = path_to_driver
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)
    return driver   


def create_soup(url):
    """create bs4 object"""
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36"})
    return BeautifulSoup(r.content, "html5lib")


def queryJobs(driver, jobTitle, jobLocation):
    """given an active driver, searches & scrapes job postings into dictionary """
    # go to url & search for jobs ordered by last 7 days, 500 jobs/page & most recent first 
    query_url  = 'https://www.careeronestop.org/JobSearch/job-Search.aspx'
    driver.get(query_url)
    driver.find_element_by_id('txtLocation').clear()
    driver.find_element_by_id('txtLocation').send_keys(jobLocation)
    driver.find_element_by_id('txtOccupation').clear()
    driver.find_element_by_id('txtOccupation').send_keys(jobTitle)
    driver.find_element_by_id('btnFindJob').click()
    driver.get(driver.current_url + '&datfilter=7' + '&pagesize=500' + '&sortcolumns=accquisitiondate&sortdirections=DSC')
    
    # get current url to scrape all links 
    searchResultsUrl = driver.current_url
    
    searchResultsSoup = create_soup(searchResultsUrl)
    table = searchResultsSoup.find('div', {'class':'datagrid no-more-tables'})
    body = table.find('tbody')
    
    # create separate lists & zip into dictionary 
    company = [i.get_text() for i in body.find_all('td', {'data-title': 'Company'})]
    title = [i.get_text() for i in body.find_all('td', {'data-title': 'Job Title'})]
    location = [i.get_text() for i in body.find_all('td', {'data-title': 'Location'})]
    title1 = [i.strip() for i in title]
    url = [i['href'] for i in body.find_all('a', {'target': '_blank'})]
    
    jobsDict = {z[0]:list(z[1:]) for z in zip(url,title1,company, location)}
    return jobsDict


def create_db_table(full_path_to_db):
    """create database table & names columns"""
    conn = sqlite3.connect(full_path_to_db)
    c = conn.cursor()
    c.execute('''CREATE TABLE career_jobs
        (id integer primary key, data, 
        company_name text, 
        job_title text)''')

    conn.commit()
    conn.close()

def create_db_table_applied(full_path_to_db):
    """create database table & names columns"""
    conn = sqlite3.connect(full_path_to_db)
    c = conn.cursor()
    c.execute('''CREATE TABLE career_jobs_applied
        (id integer primary key, data, 
        url text)''')

    conn.commit()
    conn.close()

def filterJobTitles(jobsDict, keywordsList, all_=True):
    """any=True, all=False = matches all 
       any=True, all=True = matches any"""
    updatedJobsDict = {}
    anyCount = 0
    allCount = 0
    for k,v in jobsDict.items():
        lower = v[0].lower()
        if all_:
            if all(word in lower for word in keywordsList):
                allCount+=1
                updatedJobsDict[k] = v
        else:
            if any(word in lower for word in keywordsList):
                anyCount+=1
                updatedJobsDict[k] = v
    
    if allCount > 0:
        print('Searching for all word to match')
    if anyCount > 0:
        print('Searching for any words to match')
        
    if allCount == 0:
        print('No all matches found')
    if anyCount == 0:
        print('No any matches found')
      
    return updatedJobsDict


def addToDb(dbPath, jobsDict):

    uniqueURLS = []
    count = 0
    for k,v in jobsDict.items():
        URL = k
        jobTitle = v[0]
        jobCompany = v[1]
    
        conn = sqlite3.connect(dbPath)
        c = conn.cursor()

        c.execute('SELECT * FROM career_jobs WHERE (company_name=? AND job_title=?)', (jobCompany, jobTitle))
        entry = c.fetchone()

        if entry is None:
            c.execute("insert or ignore into career_jobs (company_name, job_title) values (?, ?)", (jobCompany, jobTitle))
            conn.commit()
            uniqueURLS.append(URL)
            count+=1
            print('\n{} || New Entry added\n{} - {}'.format(count, jobTitle, jobCompany))
        else:
            print ('\n>>>>>>>>>Entry found<<<<<<<<<\n', jobTitle, jobCompany)
            
    return uniqueURLS

def screenshot_stitch(driver, fname):
    

    js = 'return Math.max( document.body.scrollHeight, document.body.offsetHeight,  document.documentElement.clientHeight,  document.documentElement.scrollHeight,  document.documentElement.offsetHeight);'

    px = driver.execute_script(js)
    rangee = px / 700
    #browser.execute_script("window.scrollTo(0, %s);" % 500)
    
    base_name = '/Users/Anthony/Desktop/python_projects_clean/selenium/db/'
    os.makedirs(base_name + fname)
    count=0
    jpg_paths = []
    for i in range(round(rangee)):
        driver.execute_script("window.scrollTo(0, %s);" % count)
        #time.sleep(5)
        jpg_path = base_name + fname + '/' + fname + '_' +  str(i) + '.png'
        driver.save_screenshot(jpg_path)
        print("Saving job description screenshot in\n> {}\n\n".format(jpg_path))
        jpg_paths.append(jpg_path)
        count+= 700
    return jpg_paths


def combine_png(png_paths):

    imgs    = [ Image.open(i) for i in png_paths ]
    dir_name = os.path.dirname(png_paths[0])
    fname = os.path.basename(png_paths[0])[:-6]
    full_path = dir_name + '/' + fname + '.png'


    # pick the image which is the smallest, and resize the others to match it (can be arbitrary image shape here)
    min_shape = sorted( [(np.sum(i.size), i.size ) for i in imgs])[0][1]
    imgs_comb = np.hstack( (np.asarray( i.resize(min_shape) ) for i in imgs ) )


    # for a vertical stacking it is simple: use vstack
    imgs_comb = np.vstack( (np.asarray( i.resize(min_shape) ) for i in imgs ) )
    imgs_comb = Image.fromarray( imgs_comb)
    imgs_comb.save(full_path)
    print("Saving concatenated job description screenshot in\n> {}\n\n".format(full_path))
    
    [os.remove(i) for i in png_paths]

def driver_screenshot(driver_path, url, fname):
    
    driver= setup_webdriver(driver_path)
    driver.get(url)
    paths = screenshot_stitch(driver,fname)
    combine_png(paths)


def addToDbApplied(driver_path, dbPath, url, fname):
    
    conn = sqlite3.connect(dbPath)
    c = conn.cursor()

    c.execute('SELECT * FROM career_jobs_applied WHERE (url=?)', (url,))
    entry = c.fetchone()
    
    
    if entry is None:
        c.execute("insert or ignore into career_jobs_applied (url) values (?)", (url,))
        conn.commit()
        print('\nNew Entry added\n{}'.format(url))
        driver_screenshot(driver_path, url, fname)
    else:
        print ('\n>>>>>>>>>Entry found<<<<<<<<<\n', url)
    

def scrapeOneStop(driverPath, jobTitle, jobLocation, dbPath, firstTable=None, 
                  all_=None, keywordsList=None):
    
    """combines all functions"""
    driver = setup_webdriver(driverPath)
    
    if firstTable:
        create_db_table(dbPath)
    
    jobsDict = queryJobs(driver, jobTitle, jobLocation)
    
    if keywordsList:
        jobsDict = filterJobTitles(jobsDict, all_=all_, keywordsList=keywordsList) 
        
    if len(jobsDict) == 0:
        print('No matches found.  Try the any/all instead of all/any')
        input('Press enter to exit.')
        sys.exit(1)
    uniqueURLS =  addToDb(dbPath, jobsDict)
  
    for idx,i in enumerate(uniqueURLS):
        concatURL = 'window.open("' + i + '","_blank");'
        driver.execute_script(concatURL)
        print('\nShowing ', idx, ' of ', len(uniqueURLS))
        if idx %10 == 0:
            input('Press enter to continue')





# user inputs 
dbApply = input('\nCheck to see if job was already applied to? y/n\n> ')
driverPath = input('\nEnter FULL PATH to web driver\n> ')
dbPath = input('\nEnter FULL PATH to databse ending with .sqlite\n> ')
dbCreate = input('\nIs this a new database? true/false\n> ')
dbCreateBoolApply = json.loads(dbCreate)
if dbApply == 'y':
    urlApply = input('\nEnter url to be added to database.\n> ')
    screenshotFname = input('\nEnter filename for screenshot.\n> ')
    if dbCreateBoolApply == True:
        create_db_table_applied(dbPath)
        addToDbApplied(driverPath, dbPath, urlApply, screenshotFname)
        #driver_screenshot(driverPath, urlApply, screenshotFname)
        sys.exit(1)
    else:
        #addToDbApplied(dbPath, urlApply)
        addToDbApplied(driverPath, dbPath, urlApply, screenshotFname)
        #driver_screenshot(driverPath, urlApply, screenshotFname)
        sys.exit(1)

jobTitle = input('\nEnter job title to search\n> ')
jobLocation = input('\nEnter job location\n> ')
filterOrNot = input('\nFilter job titles by keywords? y/n\n> ')


# logic
dbCreateBool = json.loads(dbCreate)
if filterOrNot in ['y', 'yes']:
    typeMatch = input('\nMatch all of the words in keywords? true/false\n> ')
    keywords = input('\nEnter space delimited list of keywords.\ne.g. junior software python\n> ')
    
    # format inputs for functions 
    matchList = list(keywords.split())
    bools = json.loads(typeMatch)

    if dbCreate == 'true' and bools == True:
        scrapeOneStop(driverPath, jobTitle, jobLocation, dbPath,
                      firstTable=dbCreateBool, all_=True, keywordsList=matchList)
        input('Press enter to exit')
        
    elif dbCreate == 'true' and bools !=True:
        scrapeOneStop(driverPath, jobTitle, jobLocation, dbPath,
                      firstTable=dbCreateBool, all_=False, keywordsList=matchList)
        input('Press enter to exit')
        
    elif dbCreate == 'false' and not bools == True:
        scrapeOneStop(driverPath, jobTitle, jobLocation, dbPath, all_=True, keywordsList=matchList)
        input('Press enter to exit')

    elif dbCreate == 'false' and bools == False:
        scrapeOneStop(driverPath, jobTitle, jobLocation, dbPath, all_=False, keywordsList=matchList)
        input('Press enter to exit')

else:
    if dbCreate == 'true':
        scrapeOneStop(driverPath, jobTitle, jobLocation, dbPath, firstTable=dbCreateBool)
        input('Press enter to exit')
    else:
        scrapeOneStop(driverPath, jobTitle, jobLocation, dbPath)
        input('Press enter to exit')
