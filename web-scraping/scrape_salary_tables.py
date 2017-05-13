import requests
from bs4 import BeautifulSoup
page = requests.get('http://www.baseball-reference.com/players/a/alberma01.shtml').text


table_code = page[page.find('<table class="sortable stats_table" id="br-salaries"'):]
soup = BeautifulSoup(table_code, 'lxml')

table_body  = soup.find('tbody')
body_len= len(table_body)

for i in range(body_len):
    the_row = []
    table_row=table_body.findAll('tr')
    for tr in table_row:
        value  = tr.get_text()
        the_row.append(value)