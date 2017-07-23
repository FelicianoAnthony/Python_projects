from twilio.rest import Client
from bs4 import BeautifulSoup as bs
import urllib.request
import urllib
import time

class jibberish:
    tw = 'https://www.reddit.com/r/botcity/comments/6p45q9/fsfsdf/'
    
    def numbalinks(self): 
        
        try: 
            page = urllib.request.urlopen(tw)
            soup = bs(page, "lxml")
            l = []
            for link in soup.find_all('a', href=True):
                li = link['href']
                if 'http' in li:
                    l.append(li)
            print('I found  ', len(l))
            print('sleeping for 30 seconds')
            time.sleep(30)
            return len(l)
        except Exception as e:
            print(str(e), 'going to sleep for 60 seconds')
            time.sleep(60)
        
    def looper(self): 

        first_count = self.numbalinks()

        print('about to enter the while loop...')
        while True:
            if first_count < self.numbalinks():
                print('beer')
                break
jib = jibberish()