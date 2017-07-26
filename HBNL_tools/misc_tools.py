#!/usr/bin/env python
import pandas as pd
import os
import csv
import fnmatch
import shutil

def LORETA_outliers(file_path, electrode_path, uv_threshold):
    '''reads txt files used for LORETA (416 rows by 61 columns) as data frame, removes any ERP amplitudes above uv_threshold, and returns problematic channels  
    Arguments: filepath = path to directory containing files to be checked 
               electrode_path = path to file with electrode names 
               uv_threshold = amplitude value to check'''
    
    #store electrode names in variable 
    with open(electrode_path, 'rt') as file:
        csv_file =csv.reader(file,delimiter=',')
        for i in csv_file:
            channel_lst = i
            
    #read txt files and use electrode names as columns           
    df = pd.read_csv(file_path, sep= '\s+', header = None)
    df.columns = channel_lst
    
    # return boolean values of whether df contains values higher or lower than +- 75 
    bool_df = (df > uv_threshold) | (df < -uv_threshold)
    
    #return a sum of total number of values higher than defined number by column 
    sum_tf = bool_df.sum()
    
    #reset index then only display columns if there's at least one cell above/below +- 75
    sum_reset = sum_tf.reset_index()
    sum_reset.columns = ['CHANNEL', '# ABOVE/BELOW THRESH']
    bad_cols = sum_reset.ix[sum_reset['# ABOVE/BELOW THRESH'] >= 1]
    bad_cols1 = bad_cols.set_index(keys='CHANNEL')
    return bad_cols1

def LORETA_parser(file_name, file_path):
    '''given an sLORETA .csv file with significant brain voxels -- groups voxels by Brodmann Area and gives frequency of voxels by Brodmann Area'''
    
    base_path = os.path.dirname(file_path)  #create base path 
    new_path = os.path.join(base_path, file_name)

    print(file_path, '\n')
    df = pd.read_csv(file_path)
    df1 = df.reset_index()
    df1.columns = df1.columns.str.strip()
    structure_df = df1['Structure'].str.strip()
    bman_df= df1['Brodmann area'].values

    #frequency of 2 df columns 
    df_tup = collections.Counter(zip(bman_df, structure_df)).most_common()

    brod_num, sig_vox = zip(*df_tup)
    df_tup.sort(key=operator.itemgetter(1), reverse=True)

    new_file = open(new_path, 'w')
    for i in sorted(df_tup, key=lambda x:x[0][0]):
        if i[1] == 1:
            z = 'There is', i[1], 'significant voxel in', i[0][1], 'Area', i[0][0]
            new_file.write(str(z).replace(',', '').replace("'", ''). replace("(", '').replace(")", '') + '\n')
        else:
            z = 'There are', i[1], 'significant voxels in', i[0][1], 'Area', i[0][0]
            new_file.write(str(z).replace(',', '').replace("'", ''). replace("(", '').replace(")", '') + '\n')
    new_file.close()
    
    
def sync_error(ev2_path, dat_path):
    """Provide file pathway of event file and dat file and function will return corrected event file.
       If ev2 file is missing an entire event then script will prompt user to fix manually"""


    #read event file as df and assign column names  
    df = pd.read_csv(ev2_path, header=None, delim_whitespace=True)
    df.columns = ['trial','type','stim1', 'stim2', 'stim3', 'latency']

    #create 2 df's and sort non_zero df to compare to dat file
    non_zero_ev2= df.loc[df['type'] > 0]
    zero_ev2= df.loc[df['type'] < 0.9] 
    non_zero_ev2.sort('trial', ascending=True, inplace=True) 

    #read dat file as df & assign column names
    lst = []
    with open(dat_path, 'r') as f:
        for line in f.readlines()[21:]:
            lst.append(line.split())
            df_dat = pd.DataFrame(lst)
            df_dat.columns=['trial','resp','type', 'correct', 'latency', 'stim']

    #if ev2 is totally missing an event then exit function 
    if len(non_zero_ev2) != len(df_dat):
        print('ev2 file is', len(non_zero_ev2), 'lines long', '\n', 
              'dat file is', len(df_dat), 'lines long', '\n',
              'dat file is', len(df_dat) - len(non_zero_ev2), 'line longer than event file')
        sys.exit()

    #replace type/stim codes column in ev2 file with stim codes column in dat file     
    non_zero_ev2['type'] = df_dat['type'].values

    #add 0's and overwrite ev2 file
    frames = [zero_ev2, non_zero_ev2]
    new_ev2_df = pd.concat(frames)
    new_ev2_df.to_csv(ev2_path ,sep = " ", index=False, header=False)
    
    return True   
    
def tracker_by_site(filepath, neuro_or_erp):
    """given a file that contains ALL tracker files for neuro or ERP in a given month -- creates
    separate text files based on site number"""

    with open(filepath,'r') as f:
        entries = map(str.strip,f.readlines())

    entries = sorted([entry.split() for entry in entries], key = lambda k: k[1])

    for entry in entries:
        ID = entry[1][0]
        with open(neuro_or_erp.format(ID),'a') as f:
            f.write(' '.join(entry) + '\n')
    return True