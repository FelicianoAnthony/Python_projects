#!/usr/bin/env python
import os
from collections import defaultdict
import collections
import pandas as pd
import re


def neuro_xml_to_df(path):
    """Given a full path to neuropsych sub folders, returns data frame of first 6 lines of xml file"""

    xml = [os.path.join(root,name) for root,dirs,files in os.walk(path) for name in files if name.endswith(".xml")]

    ids_lst=[]
    dob_lst = []
    gen_lst=[]
    test_lst =[]
    ses_lst=[]
    han_lst=[]
    for i in xml:
        with open(i) as f:
            for line in f:
                if line.startswith('  <Sub'):
                    ids_lst.extend(re.findall(r'<SubjectID>(.*?)</SubjectID>', line))
                if line.startswith('  <DOB'):
                    dob_lst.extend(re.findall(r'<DOB>(.*?)</DOB>', line))
                if line.startswith('  <Gen'):
                    gen_lst.extend(re.findall(r'<Gender>(.*?)</Gender>', line))
                if line.startswith('  <Test'):
                    test_lst.extend(re.findall(r'<TestDate>(.*?)</TestDate>', line))
                if line.startswith('  <Sess'):
                    ses_lst.extend(re.findall(r'<SessionCode>(.*?)</SessionCode>', line))
                if line.startswith('  <Hand'):
                    han_lst.extend(re.findall(r'<Hand>(.*?)</Hand>', line))

    data_set = pd.DataFrame(ids_lst, columns=["Subject ID"])
    data_set['Test_Date'] = test_lst
    data_set['DOB'] = dob_lst
    data_set['Gender'] = gen_lst
    data_set['Handedness'] = han_lst
    data_set['Run Letter'] = ses_lst

    data_set['Test_Date'] =pd.to_datetime(data_set.Test_Date)
    table = data_set.sort_values('Test_Date', ascending=True)
    print("sorting by test date...")
    return table

def restart_script():
    '''restarts neuro_files_check function when errors are found'''
    restart = input("Would you like to restart this program?")
    if restart == "yes" or restart == "y":
        neuro_files_check(path)
    if restart == "n" or restart == "no":
        print ("Script terminating. Goodbye.")


def neuro_files_check(path):
    '''Given a path to directory of neuropsych folders -- checks ID/SESSION across extensions in each folder and within xml files, 
       checks exp_names and version'''

    print('\n', '_______________________________Checking to see if all files extensions are present_______________________________')
    
    #checks for unknown file types
    for r,d,f in os.walk(path):
        for n in f:
            if not n.endswith(("xml", "txt", "_sum.txt")):
                path  = os.path.join(r,n)
                print('Error: Unknown file types found --', path)

    #check for all IDS have 8 numbers and all sum/txt files having CBST/TOLT in filename
    for r,d, f in os.walk(path):
        for n in f:
            if n.endswith(("_sum.txt", 'txt')):
                split = n.split("_")
                if split[1] == 'CBST':
                    pass
                elif split[1] == 'TOLT':
                    pass
                else:
                    print('Fix experiment name for ID most similar to ', n)
                    restart_script()
                if len(split[0]) != 8:
                    print(n, '---> Sub ID length incorrect')
                    restart_script()               
    
    #create dicts of ID & extension
    txt_dict = {}
    sum_dict = {}
    xml_dict = {}
    for r,d,f in os.walk(path):
        for n in f:
            all_spl = n.split("_")
            if n.endswith("_sum.txt") and all_spl:
                sum_split = n.split("_")
                sum_dict.setdefault(sum_split[0], []).append(sum_split[4])
            elif n.endswith("xml"):
                xml_split = re.split(r'[_.]', n)
                xml_dict.setdefault(xml_split[0], []).append(xml_split[3])
            elif n.endswith('.txt'):
                txt_split = re.split(r'[_.]', n)
                txt_dict.setdefault(txt_split[0], []).append(txt_split[4])
                    
    #checks for correct number of files in each folder   
    for k,v in txt_dict.items():
        if len(k) != 1 and len(v) != 2:
            print(k, 'is missing text files')

    for k,v in sum_dict.items():
        if len(k) != 1 and len(v) != 2:
            print(k, 'is missing sum.txt files')

    for k,v in xml_dict.items():
        if len(k) != 1 and len(v) != 1:
            print(k, 'is missing .xml file')

    if len(txt_dict) != len(sum_dict):
        print('There are more txt than sum.txt files for', set(txt_dict).difference(sum_dict))
    if len(sum_dict) != len(txt_dict):
        print('There are more txt than sum.txt files for', set(sum_dict).difference(txt_dict))

    #parse xml file to compare ID/session within file to compare to ID/session in xml filename itself
    xml = [os.path.join(root,name) for root,dirs,files in os.walk(path) for name in files if name.endswith(".xml")]
    within_xml_id=[]
    within_xml_run =[]
    xml_filename_id=[]
    xml_filename_run = []

    for i in xml:
        with open(i) as f:
            for line in f:
                if line.startswith('  <Sub'):
                    within_xml_id.extend(re.findall(r'<SubjectID>(.*?)</SubjectID>', line)) #need to also extract xml id from file name
                    xml_f_split = re.split(r'[\\_.]', i)    #####  pay close attention 
                    xml_filename_id.append(xml_f_split[-4]) #####  to these 3 
                    xml_filename_run.append(xml_f_split[-3])#####   lines 
                if line.startswith('  <Sess'):
                    within_xml_run.extend(re.findall(r'<SessionCode>(.*?)</SessionCode>', line))

    inside_xml = dict(zip(within_xml_id, within_xml_run))
    outside_xml = dict(zip(xml_filename_id, xml_filename_run))

    #check for xml within xml and xml filename
    for k,v in inside_xml.items():
        try:
            if inside_xml[k] != outside_xml[k]:
                print('ERROR: see xml file for run letter', k, inside_xml[k], '\n')
                restart_script()
        except Exception as e:
            print ('ERROR: check inside xml or filename xml for id most similar to', str(e))
            restart_script()


    print('\n', '_______________________________Checking to make sure txt/sum.txt IDs match xml ID_______________________________')

    for k in txt_dict:
        if k not in outside_xml.keys():
            print('ERROR: txt file with ID most similar to', k, 'doesnt match xml')
            restart_script()

    for k in sum_dict:
        if k not in outside_xml.keys():
            print('ERROR: sum.txt file with ID most similar to', k, 'doesnt match xml')
            restart_script()
            
            
    print('\n', '_______________________________Checking to make sure run letters all match_______________________________')


    #create dictionary of sum.txt and txt file IDs
    allrun_dict ={}
    for root, dirs, files in os.walk(path):
        for name in files:
            if not name.endswith("xml"):
                all_files = re.split(r'[_.]', name)
                #print(all_files)
                allrun_dict.setdefault(all_files[0], []).append(all_files[3][0])

    #check to make sure each ID has 4 of the same run letters
    #stop if they dont because in the next part we will compare the run letter to xml run letter 
    for k,v in allrun_dict.items():
        if len(allrun_dict[k]) == 4 and len(set(allrun_dict[k])) == 1:
            pass
            #print('All run letters match for', k)
        else:
            print('ERROR: Check these IDs/most similar to', k, allrun_dict[k])
            restart_script()

    #now that we know all txt files have same ID and same run letter, we compare this to xml dict
    for k,v in allrun_dict.items():
        if allrun_dict[k][0] != outside_xml[k]:
            print('ERROR: check folder', k)
        else:
            pass

def md5(path):
    '''generate md5 checksum - -read file in binary mode'''
    with open(path, "rb") as f:
        data = f.read()
        md5_return = hashlib.md5(data).hexdigest()
        return md5_return
    
    
def md5_check_walk(dir_path):
    '''given a dir path -- comapres md5 checksums across files and identifies duplicate files'''
    md5_dict = defaultdict(list)
    for r,d,f in os.walk(dir_path):
        for n in f:
            fp = os.path.join(r,n)
            md5_dict[md5(fp)].append(fp)
            
    for k,v in md5_dict.items():
        if len(v) > 1:  #multiple values for the same key
            print(len(v), 'Duplicate files:', v,'\n\n\n', 'with checksum', '\n', k)
        elif len(v) < 1:
            print('No duplicates found')