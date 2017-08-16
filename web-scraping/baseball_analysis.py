from bokeh.charts import Bar, Scatter, output_file, show, output_notebook, Histogram
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.models import HoverTool
from collections import OrderedDict
import urllib.request
import requests
from bs4 import BeautifulSoup
import pandas as pd
from glob import glob
import string
import re
import os

output_notebook()

class html_table_scraper:
    '''class provides functions which can be used to scrape, 
       merge html tables from baseball-reference,
       and plot data'''
    
    def scrape_batting_tables(self,url):
        '''Scrapes "TEAM BATTING" html table into pandas data frame'''
        self.url = url
        
        # create bs object
        r = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(r, "lxml")
        
        # get year & team name from url
        team_abbrev = re.split(r'[/.]', self.url)[6]
        year_url = re.split(r'[/.]', url)[-2]
        
        # find table, find header, find rows
        table = soup.find('div', attrs={'class': 'overthrow table_container'})
        table_head = table.find('thead')

        # create table header list
        header = []    
        for th in table_head.findAll('th'):
            key = th.get_text()
            header.append(key)

        # find number of 'empty' rows
        endrows = 0
        for tr in table.findAll('tr'):
            if tr.findAll('th')[0].get_text() in (''):
                endrows += 1

        # find number of rows in table
        rows = len(table.findAll('tr'))
        rows -= endrows + 1  

        # create lists of row data, create ordered dictionary from header and row data...
        # ...create list of dictionaries for data frame
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

        # create df & change column names to all uppercase for easy searching 
        df = pd.DataFrame(list_of_dicts)
        df.columns = [col.upper() for col in df.columns]
        
        # add team column 
        df['TEAM_NAME'] = team_abbrev
        df['YEAR'] = year_url

        #strip all bad characters from NAME column to allow searching by name & index
        df['NAME'] = df['NAME'].str.replace(r'\(([^()]+)\)', '')
        df['NAME'] = df['NAME'].str.replace('*', '')
        df['NAME'] = df['NAME'].str.replace('#', '')
        
        # format dtypes -- float needed 0 before decimal
        df1 = self.set_batting_dtypes(df, 'BA')
        df2 = self.set_batting_dtypes(df1, 'OPS')
        df3 = self.set_batting_dtypes(df2, 'OBP')
        df4 = self.set_batting_dtypes(df3, 'SLG')
        
        
        return df4.set_index(keys=['NAME', 'TEAM_NAME', 'YEAR'])

    def get_team_names(self, base_url, year_as_str):
        '''returns a list of team name abbreviations used in baseball reference tables
           Args: years_as_str = str(/2016)'''
        
        self.base_url = base_url
        self.year_as_str = year_as_str
        
        # use pandas to get table
        base = 'http://www.baseball-reference.com/leagues/MLB/'
        ext = '.shtml'
        full_url = base + year_as_str + ext
        df = pd.read_html(full_url, flavor='html5lib', attrs={'class': 'sortable'})

        df_names = df[0]

        teams= df_names['Tm'].tolist()
        del teams[-2:]
        return ['/' + i  for i in teams] 
    
    def create_batting_links(self, base_url, team_names, years, extension):

        '''scrapes batting tables and saves to csv
        Args: str(base_url)
              list(team_name)
              list(year)
              str(extension)'''
        
        self.base_url = base_url
        self.team_names = team_names
        self.years = years 
        self.extension = extension
        
        # concat urls & append to list 
        links_lst = []
        for y in years:
            for n in team_names:
                links_lst.append(base_url + n + y + extension)
                
        # so you know when to stop
        count = 0
        print('Saving in ', 'os.getcwd()', '\n')
        while count < len(links_lst):

            df = self.scrape_batting_tables(links_lst[count])
            file_name = links_lst[count][40:48].replace('/', '_')
            df.to_csv('batting_' + file_name + '.csv')
            count += 1
            print('Saved csv for team_year - ' + file_name)

            
    def get_player_names(self, fp, stats=None):
        '''given a file path that has ALL batting stats for a specific team or teams, 
           concatenates all csvs into a giant data frame -- folder must ONLY have batting csvs '''
    
        self.fp = fp
    
        # wont search recursively 
        csv_paths = glob(fp + '/*csv')

        df_lst = []
        for csv in csv_paths:
            df = pd.read_csv(csv)
            df_lst.append(df)

        d_f = pd.concat(df_lst)
        df = d_f.fillna(value=0)
        
        # change dtypes
        objects = [i for i in df.columns if i.startswith(('NAME', 'TEAM_NAME', 'POS'))]
        floats = [i for i in df.columns if i.startswith(('OBP', 'SLG', 'OPS', 'BA'))]

        # whats left over are integers
        obj_flts = objects + floats
        ints = [i for i in df.columns if i not in obj_flts]

        # convert ints
        df[ints] = df[ints].astype(int)
        stats_all = df
        
        if stats:
            return stats_all

        all_player_names = stats_all['NAME'].tolist()
        sorted_names = sorted(all_player_names, key=lambda x: x.split(" ")[-1])
        return sorted_names
    
    def scrape_salary_table(self, player_url):
        '''scrapes salary table as multi-index data frame, optional arg to save as csv'''
    
        self.player_url = player_url
        try: 
            page = requests.get(player_url).text
            table_code = page[page.find('<table class="sortable stats_table" id="br-salaries"'):]
            soup = BeautifulSoup(table_code, 'lxml')

            #second bs4 soup
            r = urllib.request.urlopen(player_url).read()
            normal_soup = BeautifulSoup(r, 'lxml')


            table_body  = soup.find('tbody')
            # get player, team, position
            for i in normal_soup.find_all('h1'):
                for j in i:
                    player_name = i.get_text() 

            #find team name 
            for p in normal_soup.find_all('p'):
                for i in p.find_all('a'):
                    if '/teams' in i['href']: 
                        team_name = i['href'][7:10]

            # get position 
            for p in normal_soup.find_all('p'):
                if 'Position' in p.get_text():
                    pos = p.get_text()

            split = pos.split(':')[1]
            position = split.strip()

            # height and weight        
            weight = normal_soup.find('span',{'itemprop':'weight'}).text
            height = normal_soup.find('span',{'itemprop':'height'}).text
            height2 = height[0] + "'" + height[2]

            # get salaries 
            sal = [j.get_text() for i in table_body.find_all('tr') for j in i.find_all('td') if j['data-stat'] == 'salary']
            salary_lst = [i.replace('$', '').replace('*', '') for i in sal]

            # get years             
            years = table_body.findAll('th')                          
            years_lst = [i.get_text() for i in years]
            del years_lst[-1]

            # create a dictionary of dictionaries
            salary_dict = {}
            salary_dict[player_name] = {}
            salary_dict[player_name]['years'] = years_lst
            salary_dict[player_name]['salary'] = salary_lst

            split = pd.DataFrame.from_dict(salary_dict, orient = 'index')

            # explodes a list into rows
            years_col = split.years.apply(lambda x: pd.Series(x)).unstack()
            salary_col= split.salary.apply(lambda x: pd.Series(x)).unstack()

            # concat one series to df then add other series to existing df
            df = years_col.to_frame()
            df['SALARY'] = salary_col
            df2 = df.reset_index()
            df3= df2.rename(columns = {0: 'YEAR', 'level_1': 'NAME'})

            del df3['level_0']
            df3['TEAM_NAME'] = team_name
            df3['POSITION'] = position
            df3['HEIGHT'] = height2
            df3['WEIGHT'] = weight
            df4 = df3.set_index(keys = ['NAME', 'TEAM_NAME', 'YEAR'])
            df4.to_csv(player_name  +'.csv')
            
        except Exception as e:
            print(str(e), '^^  -- salary table probably missing -- ')
            pass

        
    def pd_convert_float(self, df, col):
        '''takes a pd column and converts it to a float returns new df'''
        self.df = df
        self.col = col

        # append 0 and set return as column
        slg = df[col].tolist()
        slg_float = ['0' + i for i in slg]
        df[col] = slg_float
        df[col]= df[col].astype(float)
        return df

    
    def set_batting_dtypes(self, df, col):
        '''index must be reset before passing '''
        
        self.df = df
        self.col = col

        # sort column names into dtypes
        objects = [i for i in df.columns if i.startswith(('NAME', 'TEAM_NAME', 'POS'))]
        floats = [i for i in df.columns if i.startswith(('OBP', 'SLG', 'OPS', 'BA'))]

        # whats left over are integers
        obj_flts = objects + floats
        ints = [i for i in df.columns if i not in obj_flts]

        # convert ints
        df[ints] = df[ints].astype(int)

        # pass into function that adds 0 before deciaml point 
        df1 = self.pd_convert_float(df, col)
        return df1

        
        
    def salary_crawl(self, player_name_lst):
        '''given a list of players, search player index on baseball-reference
           to scrape entire salary table'''
        
        self.player_name_lst = player_name_lst
        url = 'http://www.baseball-reference.com/players/'
        alpha = string.ascii_lowercase ###change this

        abcc = [i + '/' for i in alpha]
        
        print('Saving in ', 'os.getcwd()', '\n')
        
        # player name from df has a space at the end
        player_names =[i[:-1] for i in player_name_lst]

        
        missing_names = []
        for letter in abcc:
            base_url = url + letter
            r = urllib.request.urlopen(base_url).read()
            soup = BeautifulSoup(r, 'lxml')
            for p in soup.find_all('p'):
                for i in p.find_all('a'):
                    if '/players' in i['href']:
                        if i.get_text() in player_names:
                            shtml = i['href'][9:]
                            new_url = url + shtml
                            print(new_url)
                            self.scrape_salary_table(new_url)
                        else:
                            missing_names.append(i.get_text())

    
    def merge_dfs(self, salary_path, team_path, year):
        '''salary df with team df on name, team, and year'''
        self.salary_path = salary_path
        self.team_path = team_path
        self.year = year

        # create data frame from team csvs
        team_path = glob(team_path  + '/batting*csv')


        df_lst = []
        for csv in team_path:
            df = pd.read_csv(csv)
            df_lst.append(df)
        teams_df = pd.concat(df_lst)
        team_df= teams_df.rename(columns = {'YEAR': 'YEARS'})

        # create data frame from player salaries
        salaries  = glob(salary_path + '/*csv')
        df_sal = []
        for csv in salaries:
            df1 = pd.read_csv(csv)
            df_sal.append(df1)
        sal_df = pd.concat(df_sal)

        # format salary df for merge 
        sal_df1 = sal_df.dropna(axis=0)
        sal_df1['YEARS'] = sal_df1['YEARS'].astype(int) # see pd_concat_flaot if doesnt work 
        sal_df2 = sal_df1[sal_df1['YEARS'] == year]
        sal_df3 = sal_df2[sal_df2['SALARY'] > '0']
        
        # merges ONLY if name, team, year found in team_df table
        return pd.merge(team_df, sal_df3, on=['NAME', 'TEAM_NAME', 'YEARS'], how='inner')
    
    def sum_team_stats(self, df, col_to_sum, team_name):
        ''' sums up a specific statistic for every team and appends that value to a dictionary'''
    
        self.df = df
        self.col_to_sum = col_to_sum
        self.team_name  = team_name

        sum_col =  df.loc[df['TEAM_NAME'] == team_name, col_to_sum].sum()

        d = {}
        d[team_name + '_' + col_to_sum + '_total'] = sum_col
        return d

    def sum_stat_by_team(self, df_path, year_int, stat, 
                         filter_gt_by=None, filter_lt_by=None, 
                         get_plot_df = None, get_cols = None):
    
        '''year = 2016
           stat=2b
           filter_by = AB
           '''
        
        self.path = df_path
        self.year_int = year_int
        self.stat = stat
        self.filter_gt_by = filter_gt_by
        self.filter_lt_by = filter_lt_by
        self.get_cols = get_cols
        self.get_plot_df = get_plot_df
        
        # find batting_year csvs
        files_lst = glob(df_path + '/batting*csv')


        # append vertically 
        df_lst = [pd.read_csv(i) for i in files_lst]
        df = pd.concat(df_lst)

        # get column names
        if get_cols:
            return df.columns


        # filter column related to column of interest by 
        if filter_gt_by:
            df = df[df[filter_gt_by[0]] >= filter_gt_by[1]].sort_values(filter_gt_by[0], ascending=True)
        if filter_lt_by:
            df = df[df[filter_lt_by[0]] <= filter_lt_by[1]].sort_values(filter_lt_by[0], ascending=False)

        # filter by year    
        df_2016 = df[df['YEAR'] == year_int]

        teamz = list(set(df_2016.TEAM_NAME.tolist()))    

        # this function returns a dictionary for the sum of a given stat for each team 
        sums = {}
        for i in teamz:
            dic = self.sum_team_stats(df_2016, stat, i)
            sums.update(dic)
            
        # create new df from new dictionary
        df_2b = pd.DataFrame.from_dict(sums, orient='index').reset_index()

        #create a new team names column
        t = df_2b['index'].tolist()
        tt = [i[:3] for i in t]
        df_2b['TEAM_NAME'] = tt
        df2b = df_2b.rename(columns={0: stat})  

        # inspet df before plotting
        if get_plot_df:
            return df2b
        #plot
        p = Bar(df2b, label='TEAM_NAME', values=stat, agg='sum', 
                title=str(year_int) + ' ' + stat + ' summed', legend=False)
        return show(p)
    
    def scatterplot_salary(self, merged_sal, sal_lower_range, sal_upper_range, filter_by_statnum_tup,
                          get_plot_df = None):
        '''ARGS: str(merged_sal) = merged data frame of teams and salary 
                 int(sal_lower_range) = lower range of salary
                 int(sal_upper_range) = upper range of salary
                 tuple(filter_by_statnum_tup) = tuple of stat as string & num as int --> ex: ('G', 20)'''
        
        self.merged_sal = merged_sal
        self.sal_lower_range = sal_lower_range
        self.sal_upper_range = sal_upper_range
        self.filter_by_statnum_tup = filter_by_statnum_tup
        self.get_plot_df = get_plot_df

        # fill NaN, change dtypes of specific columns, format salary column for hover tools & plot
        cols = merged_sal.columns.tolist()
        merged_sal1 = merged_sal.fillna(value=0)
        sal_lst = merged_sal1['SALARY'].tolist()
        sal_lst_dollar = ['$' + i for i in sal_lst]
        merged_sal1['PLOT_SALARY'] = sal_lst_dollar
        merged_sal1['SALARY'] = merged_sal1['SALARY'].str.replace(',', '')
        int_cols = [i for i in merged_sal1.columns if not i.startswith(('NAME', 'POS','TEAM_NAME' ,'year', 'HEIGHT', 'WEIGHT', 'PLOT_SALARY'))]
        merged_sal1[int_cols] = merged_sal1[int_cols].astype(int)

        # filtering by
        reduced_sal = merged_sal1[(merged_sal1['SALARY']  < sal_upper_range) & (merged_sal1['SALARY'] > sal_lower_range)]
        reduced_game_sal = reduced_sal[reduced_sal[filter_by_statnum_tup[0]] > filter_by_statnum_tup[1]]
        
        # see what's being plotted 
        if get_plot_df:
            return reduced_game_sal
        
        # data
        source = ColumnDataSource(data=dict(x=reduced_game_sal[filter_by_statnum_tup[0]],y=reduced_game_sal['SALARY'],desc=reduced_game_sal['NAME'], desc1=reduced_sal['POS'], desc2=reduced_game_sal['PLOT_SALARY'], desc3=reduced_game_sal['TEAM_NAME']))

        # pandas column named mapped to hovertools shows up over each glyph
        hover = HoverTool(
                tooltips=[
                    ("Player", " @desc"),
                    ("POS", " @desc1"),
                    ("SALARY", ' @desc2'),
                    ("TEAM", ' @desc3')
                ]
            )
        # change dimensions 
        p = figure(plot_width=650, plot_height=500, tools=[hover])

        # changes gridline colors 
        #p.xgrid.grid_line_color = 'white'
        #p.ygrid.grid_line_color = 'white'

        # set axes and title 
        p.title = "{} {} {} {}".format("Salary vs", filter_by_statnum_tup[0],  "         n=" , str(len(reduced_game_sal)))
        p.xaxis.axis_label = filter_by_statnum_tup[0]
        p.yaxis.axis_label = 'Salary'

        # define type of glyph to use and color...
        p.circle('x', 'y', size=10, source=source, color = 'black', line_color='white', alpha= 0.5)

        # output_notebook() before this
        return show(p)
    
    
    def stat_divided_by_stat(self, team_path, first_stat_tup, 
                             second_stat_tup, year_int, bins_int,
                             get_plot_df=False): 
        '''ARGS: team_path = path to ALL BATTING CSVS on computer
                 fir = ('AB', 20)
                 sec = ('SO', 5)
                 int(year)'''

        self.first_stat_tup = first_stat_tup
        self.second_stat_tup = second_stat_tup
        self.year_int = year_int
        self.team_path = team_path
        self.get_plot_df = get_plot_df
        self.bins_int = bins_int

        new_col_name = first_stat_tup[0] + '_' + second_stat_tup[0]

        all_df = self.get_player_names(team_path, stats=True)
        years_df = all_df[all_df['YEAR'] == year_int]
        years_df1 = years_df.ix[(years_df[first_stat_tup[0]] > first_stat_tup[1]) & (years_df[second_stat_tup[0]] > second_stat_tup[1])]


        years_df1[new_col_name] = years_df1[first_stat_tup[0]] / years_df1[second_stat_tup[0]]
        filted1 = years_df1[years_df1[new_col_name] != 0]
        filted1[new_col_name] = filted1[new_col_name].round()
        
        if get_plot_df:
            return filted1

        p = Histogram(filted1, new_col_name, title= new_col_name + "Distribution" + '        n=' + str(len(filted1)), bins=bins_int)
        return show(p)
    
#table_scraper = html_table_scraper()