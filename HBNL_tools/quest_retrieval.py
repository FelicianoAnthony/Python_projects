#!/usr/bin/env python

import sys
sys.path.append('/export/home/exp/python/dev/')
from db.quest_import import sasdir_tocsv, map_ph4, map_ph4_ssaga

import requests
from urllib.request import urlopen 
import zipfile
import os
import shutil


def zork_retrieval(user_name, password, distro_num, target_base_dir= '/active_projects/anthony/zork'):
    '''Downloads most recent distribution of questionnaire data to directory of users choice'''
   
    #create full urls from dictionary 
    base_url = 'https://zork5.wustl.edu/coganew/data/available_data'
    url_lst = []
    for k in map_ph4:
        url_lst.append(base_url + map_ph4[k]['zork_url'])
    for k in map_ph4_ssaga:
        url_lst.append(base_url + map_ph4_ssaga[k]['zork_url'])

    #create subject and session directories
    folder_names = 'session', 'subject'
    for name in folder_names:
        new_folders=os.path.join(target_base_dir, distro_num, name)
        if not os.path.exists(new_folders):
            os.makedirs(new_folders)
            
    #store "base paths" so they're easier to call later
    path = os.path.join(target_base_dir, distro_num)
    sess_dir = os.path.join(path, folder_names[0])
    sub_dir = os.path.join(path, folder_names[1])
    
    #log in and download zip files 
    for i in url_lst:
        try:
            login_info = requests.get(i, auth=(user_name, password))
        except:
            print("Invalid Login")
        #error check -- if url doesnt exist then print missing zip???
        zip_names = i.split('/')[-1]
        with open(os.path.join(path, zip_names), 'wb') as zips:
            zips.write(login_info.content)
            print ('Downloading ' + '||' + zip_names + '||')
            
    #moves zip files to subject or session directory
    for file in os.listdir(path):
        for k in map_ph4:
            if file.startswith(map_ph4[k]['zip_name']):
                shutil.move(os.path.join(path, file), sess_dir)
        os.chdir(os.path.join(path, folder_names[1]))
        for k in map_ph4_ssaga:
            if file.startswith(map_ph4_ssaga[k]['zip_name']):
                shutil.move(os.path.join(path, file), sub_dir)
    
    #create subdirectories named after questionnaires 
    for file in os.listdir(sess_dir):
        for k in map_ph4:
            if file.startswith(map_ph4[k]['zip_name']):
                if not os.path.exists(os.path.join(sess_dir, k)):
                    os.makedirs(os.path.join(sess_dir,k))
                    shutil.move(os.path.join(sess_dir, file), os.path.join(sess_dir, k,file))
                    
    for file in os.listdir(sub_dir):
        for k in map_ph4_ssaga:
            if file.startswith(map_ph4_ssaga[k]['zip_name']):
                if not os.path.exists(os.path.join(sub_dir, k)):
                    os.makedirs(os.path.join(sub_dir,k))
                    shutil.move(os.path.join(sub_dir,file), os.path.join(sub_dir,k,file))
                    
    #unzip files in their current directories
    for roots, dirs, files in os.walk(path):
        for name in files:
            if name.endswith(".zip"):
                zipfile.ZipFile(os.path.join(roots, name)).extractall(os.path.join(roots))
                print('Unzipping ' + '||' + name + '||')    

    #removes spaces between achenbach directory so its accessible, create csvs, remove zips
    for roots, dirs, files in os.walk(path):
        for name in dirs:
            if name.startswith("Achenbach"): #-----> move files up a directory??
                os.rename(os.path.join(roots,name), os.path.join(roots, name.replace(' ', '')))
            sasdir_tocsv(os.path.join(roots, name) + '/')
            print('Creating csvs for ' + '||' + name + '||')
        for name in files:
            if name.endswith('.zip'):
                os.remove(os.path.join(roots,name))

    return True