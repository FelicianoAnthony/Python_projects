import os
import sys
from glob import glob
from collections import defaultdict
from collections import Counter
import collections
import re
import shutil
import subprocess


#list of tuples of exp names associated with each extension 
dat_names = ('vp3', 'cpt', 'ern', 'ant', 'aod', 'ans', 'stp', 'gng')
cnt_names = ('eeo', 'eec', 'vp3', 'cpt', 'ern', 'ant', 'aod', 'ans', 'stp', 'gng', 'anr')
ps_names = ('vp3', 'cpt', 'ern', 'ant', 'aod', 'anr', 'stp', 'gng')
#create dictionary for .avg files 
avg_dict = {'vp3': 3,
            'gng': 2,
            'ern': 4,
            'stp': 2,
            'ant': 4,
            'cpt': 6,
            'aod': 2,
            'anr': 2}

def ext_search(path, file_ext=None, exp_names_tup=None, exp_names_dict=None,split_idx=None):
    '''str(path)
       str(file_ext)'''
    
    return [fname.split("_")[split_idx] for fname in os.listdir(path) if fname.endswith(file_ext) 
            and fname.startswith(exp_names_tup)]

def compare_dict_keys(dict1, dict2): 
    '''returns keys found in one dict but not the other'''
    
    return set(dict1.keys()) ^ set(dict2.keys())

def print_runs_info(ext_lst, file_type, dirname):
    '''prints text for folder run letter counts'''
    
    if len(ext_lst) != 0:
        print("Run letters for the", len(ext_lst),  file_type, "files in", 
        dirname, "--", set(ext_lst))
        
def print_misc_ext_counts(ext_lst, file_type):
    '''prints text for extension counts in each folder'''
    
    if len(ext_lst) > 0:
        print(len(ext_lst), file_type, 'files found', '\n')
        
        
def check_erp_version(fp, exp_name, version_num): 
    '''str(fp)
       tuple or str(exp_name)
       str(version)'''
    for r,d,f in os.walk(fp):
        for n in f:
            split = n.split('_')
            if n.startswith((exp_name)):
                if split[1] != version_num:
                    print('Check version for ', n)

def erp_extensions_check(fp):
    '''Given a filepath, returns count of extensions by experiment, 
    missing extensions by experiment, and misc. files'''
    
    print('You are in', fp,'\n')
    dirname = os.path.basename(fp)
    
    #check versions
    vp3_version = check_erp_version(fp, 'vp3', '6')
    gng_stp_version = check_erp_version(fp, ('gng','stp'), '3')
    ans_anr_version = check_erp_version(fp, ('anr', 'ans'), '5')
    aod_version = check_erp_version(fp, 'aod', '7')
    cpt_version = check_erp_version(fp, 'cpt', '4')
    ern_version = check_erp_version(fp, 'ern', '9')
    
    #core files - extension
    avg_lst = ext_search(fp, '.avg', exp_names_tup=ps_names, split_idx=0)#check this out 
    dat_lst = ext_search(fp, '.dat', exp_names_tup=dat_names, split_idx=0)
    cnt_lst = ext_search(fp, '_32.cnt', exp_names_tup=cnt_names, split_idx=0)
    avg_ps_lst = ext_search(fp, '_avg.ps', exp_names_tup=ps_names, split_idx=0)

    #HBNL files - extension
    h1_ps_lst = ext_search(fp, '.h1.ps', exp_names_tup=dat_names,split_idx=0)
    avg_h1_lst = ext_search(fp, '_avg.h1', exp_names_tup=dat_names,split_idx=0) #special case

    #to be removed files - extension
    cnt_rr_lst = ext_search(fp, '_rr.cnt', exp_names_tup=cnt_names,split_idx=0)
    cnt_h1_lst = ext_search(fp, '_cnt.h1', exp_names_tup=cnt_names, split_idx=0)
    orig_cnt_lst = ext_search(fp, '_orig.cnt', exp_names_tup=cnt_names, split_idx=0)
    bad_orig_lst = ext_search(fp, '_32_original.cnt', exp_names_tup=cnt_names, split_idx=0)
    ev2_lst = ext_search(fp, '.ev2', exp_names_tup=cnt_names, split_idx=0)
    
    #core files - run letter
    avg_run_lst = ext_search(fp, '.avg', exp_names_tup=ps_names, split_idx=2)#check this out 
    dat_run_lst = ext_search(fp, '.dat', exp_names_tup=dat_names, split_idx=2)
    cnt_run_lst = ext_search(fp, '_32.cnt', exp_names_tup=cnt_names, split_idx=2)
    avg_ps_run_lst = ext_search(fp, '_avg.ps', exp_names_tup=ps_names, split_idx=2)

    #HBNL files - run letter
    h1_ps_run_lst = ext_search(fp, '.h1.ps', exp_names_tup=dat_names,split_idx=2) #special case
    avg_h1_run_lst = ext_search(fp, '_avg.h1', exp_names_tup=dat_names,split_idx=2) #special case 
    
    
    #to be removed files - run letter
    cnt_rr_run_lst = ext_search(fp, '_rr.cnt', exp_names_tup=cnt_names,split_idx=2)
    cnt_h1_run_lst = ext_search(fp, '_cnt.h1', exp_names_tup=cnt_names, split_idx=2)
    orig_cnt_run_lst = ext_search(fp, '_orig.cnt', exp_names_tup=cnt_names, split_idx=2)
    bad_orig_run_lst = ext_search(fp, '_32_original.cnt', exp_names_tup=cnt_names, split_idx=2)

    #count total number of data files in directory 
    total_file_count = 0
    other_file_count = 0
    for file in glob(os.path.join(fp, '*.*')):
        if file.endswith(('txt', 'sub', 'db', 'ev2')):
            other_file_count += 1
        else:
            total_file_count += 1
            
    #sub id is key and file extensions is value 
    ids_dict = {}
    for file in os.listdir(fp):
        if not file.endswith(('txt', 'sub', 'db', 'ev2')):
            split_fname = re.split(r'[_.A-Z]', file )
            ids_dict.setdefault(split_fname[3], []).append(split_fname[-1])
            
    
    print('____________________________________Are Sub IDs Identical?', '____________________________________', '\n')        

    #if there is more than 1 ID for each extension then error was made       
    for k,v in ids_dict.items():
        if len(ids_dict) != 1:
            print('ERROR: One of these IDs is wrong', k, set(ids_dict.keys()), '\n')
            sys.exit(1)
        else:
            print('All IDs are the same', '\n')
            
            
            
    print('____________________________________Are Run Letters Identical?', '____________________________________' '\n')

    #most common files
    avg_runs = print_runs_info(avg_run_lst,'avg', dirname)
    avg_ps_runs = print_runs_info(avg_ps_run_lst, 'avg.ps', dirname)
    cnt_runs = print_runs_info(cnt_run_lst, '_32.cnt', dirname)
    dat_runs = print_runs_info(dat_run_lst, '.dat', dirname)

    #not so common files 
    cnt_rr_runs = print_runs_info(cnt_rr_run_lst, 'cnt_rr', dirname)
    h1_ps_runs = print_runs_info(h1_ps_run_lst, 'h1_ps', dirname)
    cnt_h1_runs = print_runs_info(cnt_h1_run_lst, 'cnt.h1', dirname)
    orig_cnt = print_runs_info(orig_cnt_run_lst,'orig.cnt', dirname)
    avg_h1_runs = print_runs_info(avg_h1_run_lst, '_avg.h1', dirname)
      
        
    answer=input('EXTENSIONS COUNTS?')
    if answer is ['y', 'Y', 'Yes', 'yes']:
        pass
    if answer is ['n', 'N', 'No', 'no']:
        sys.exit(0)

  
    print("_____________________File Extension Count By Experiment_____________________", '\n',
         len(avg_lst), '.avg files', '\n',
         len(cnt_lst), '.cnt files', '\n',
         len(dat_lst), '.dat files', '\n',
         len(avg_ps_lst), '.ps files', '\n',
         len(orig_cnt_lst), 'orig.cnt files', '\n\n',
        '_____________________Missing File Extensions By Experiment_____________________', '\n')
    
    print('Missing avg files...')
    #create dictionary from avg files in nsfolder       
    ns_avg_dict= defaultdict(int)
    for w in avg_lst:
        ns_avg_dict[w] += 1

    if len(avg_dict) == len(ns_avg_dict):
        for k,v in avg_dict.items():
            if ns_avg_dict[k] != v:
                print('{} experiment missing {} avg files'.format(k,v))
    else:
        missing_keys = compare_dict_keys(avg_dict, ns_avg_dict)
        print('Avg dicts unequal length, missing', missing_keys, 'from folder')

    if len(dat_lst) != 8:
        print('\n', 'Missing dat files =', ','.join(set(dat_names).difference(dat_lst)), '\n')
    if len(cnt_lst) != 10:
        print('Missing cnt files =', ','.join(set(cnt_names).difference(cnt_lst)), '\n')
    if len(avg_ps_lst) != 25:
        print('Missing ps files =', ','.join(set(ps_names).difference(avg_ps_lst)), '\n')

    if len(dat_lst) + len(cnt_lst) + len(avg_ps_lst) + len(avg_lst) == 51:
        print('All dat/cnt/avg.ps files accounted for')


    print('_____________________Miscellaneous Extensions_____________________')    
    
    h1_ps_counts = print_misc_ext_counts(h1_ps_lst, 'h1.ps')
    cnt_h1_counts = print_misc_ext_counts(cnt_h1_lst, 'cnt.h1')
    avg_h1_counts = print_misc_ext_counts(avg_h1_lst, 'avg.h1')
    avg_h1_ps_counts = print_misc_ext_counts(h1_ps_lst, 'avg.h1.ps')
    ev2_counts = print_misc_ext_counts(ev2_lst, 'ev2')
    cnt_rr_counts = print_misc_ext_counts(cnt_rr_lst, 'cnt_rr')
    bad_orig_counts = print_misc_ext_counts(bad_orig_lst, 'mislabeled original')
    return True

def erp_and_filesize_check(fp_check):
    '''given a path to a directory of ns folders,
       runs ERP-raw-data_check.sh & DVD-file-size_check.sh scripts,
       and prints stdout'''
    
    for r,d,f in os.walk(fp_check):
        for n in d:
            dirs = os.path.join(r,n)
            erp_check = subprocess.Popen('ERP-raw-data_check.sh {}'.format(dirs), shell=True, 
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dirs)
            result_erp = erp_check.communicate()[0]
            print('ERP CHECK:', dirs, result_erp.decode('ascii'))
            size_check = subprocess.Popen('DVD-file-size_check.sh {}'.format(dirs), shell=True, 
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dirs)
            result_size = size_check.communicate()[0]
            print('FILE SIZE CHECK: ', dirs, result_size.decode('ascii'))

def erp_extensions_removal(filepath):
    '''input can be list of file paths.
    searches for h1/cnt.h1/h1.ps/ev2/mt files and prompts user for removal'''


    yes = ['yes', 'y', 'Y', 'YES']
    no = ['no', 'n', 'N', 'No' ]

    count = 0
    for root, dirs, files in os.walk(filepath):
        for name in files:
            if name.endswith(('avg.h1', 'cnt.h1', 'avg.h1.ps', 'ev2', 'mt')):
                print(count, ' --->', os.path.join(root, name))
                quest=input('Are you sure you want to delete? ')
                if quest in yes:
                    count+=1
                    os.remove(os.path.join(root,name))
                    print('Deleted', name,'\n\n')
                elif quest in no:
                    count+=1
                    print('Skipped', name,'\n\n')
                elif quest not in no or yes:
                    print('Please enter a valid response', '\n\n')