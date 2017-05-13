import pandas as pd



''''These functions use class from html_scraper_bs4.py'''
def format_team_names():
    
    '''returns a list of team name abbreviations used in baseball reference tables'''
    
    names_link = 'http://www.baseball-reference.com/leagues/MLB/2016.shtml'
    df = pd.read_html(names_link, flavor='html5lib', attrs={'class': 'sortable'})

    df_names = df[0]

    teams= df_names['Tm'].tolist()
    del teams[-2:]
    team_names = ['/' + i  for i in teams]
    
    return team_names 

    #use this function to create links
def create_links(stem, team_names, years, extension):
    
    '''this function creates links to be iterated over
       str(steem)
       [team_name]
       [year]
       str(extension)'''

    links_lst = []
    for y in years:
        for n in team_names:
            links_lst.append(stem + n + y + extension)
            
    return links_lst


#use this function to create csvs
def html_to_csv(links_list):
    
    
    length_list  =len(links_list)
    count = 0

    while count < length_list:
    
        count += 1
        df = table_scraper.scrape_br_html_table(links_list[count]) #function here 
        file_name = links_list[count][40:48].replace('/', '_')
        df.to_csv('batting_' + file_name + '.csv')
        print(links_list[count])
            


#####example usage#####

#get list of team_names
team_names = format_team_names()

#create specific team-year combinations
stem = 'http://www.baseball-reference.com/teams'
years_lst = ['/2012', '/2013', '/2014', '/2015', '/2016', '/2017']
ext = '.shtml'
team_links = create_links(stem, team_names, years_lst, ext)


#download batting tables to csv
html_to_csv(team_links)