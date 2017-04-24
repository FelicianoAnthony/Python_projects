import os
import sys
from glob import glob
from collections import defaultdict
import collections
import re
import shutil
import subprocess

def erp_extensions_check(fp):
    '''Given a filepath, returns count of extensions by experiment, 
    missing extensions by experiment, and misc. files'''

    #list of tuples of exp names associated with each extension 
    dat_names = ('vp3', 'cpt', 'ern', 'ant', 'aod', 'ans', 'stp', 'gng')
    cnt_names = ('eeo', 'eec', 'vp3', 'cpt', 'ern', 'ant', 'aod', 'ans', 'stp', 'gng')
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


    #create lists of all extensions according to their file extensions
    avg_lst = [fname.split("_")[0] for fname in os.listdir(fp) if fname.endswith("avg") and fname.startswith(ps_names)]
    avg_ps_lst = [fname.split("_")[0] for fname in os.listdir(fp) if fname.endswith("avg.ps") and fname.startswith(ps_names)]
    h1_ps_lst = [fname.split("_")[0] for fname in os.listdir(fp) if fname.endswith("h1.ps") and fname.startswith(dat_names)]
    dat_lst = [fname.split("_")[0] for fname in os.listdir(fp) if fname.endswith("dat") and fname.startswith(dat_names)]
    avg_h1_lst = [fname.split("_")[0] for fname in os.listdir(fp) if fname.endswith("_avg.h1") and fname.startswith(dat_names)]
    cnt_rr_lst = [fname.split("_")[0] for fname in os.listdir(fp) if fname.endswith("_rr.cnt") and fname.startswith(cnt_names)]
    cnt_lst = [fname.split("_")[0] for fname in os.listdir(fp) if fname.endswith("_32.cnt") and fname.startswith(cnt_names)]
    cnt_h1_lst = [fname.split("_")[0] for fname in os.listdir(fp) if fname.endswith("cnt.h1") and fname.startswith(cnt_names)]
    orig_cnt_lst = [fname.split("_")[0] for fname in os.listdir(fp) if fname.endswith("_orig.cnt") and fname.startswith(cnt_names)]
    bad_orig_lst = [fname.split("_")[0] for fname in os.listdir(fp) if fname.endswith("_32_original.cnt") and fname.startswith(cnt_names)]
    ev2_lst = [fname.split("_")[0] for fname in os.listdir(fp) if fname.endswith("ev2") and fname.startswith(cnt_names)]


    #count total number of data files in directory 
    total_file_count = 0
    other_file_count = 0
    for file in glob(os.path.join(fp, '*.*')):
        if file.endswith(('txt', 'sub', 'db')):
            other_file_count += 1
        else:
            total_file_count += 1
    total_file_count

    #create dictionary from avg files in nsfolder       
    ns_avg_dict= defaultdict(int)
    for w in avg_lst:
        ns_avg_dict[w] += 1


    #print statement is split up because try/except sometimes doesnt yield results--cant call dict every time  
    print('File information for:', fp, '\n\n',
         "_____________________File Extension Count By Experiment_____________________", '\n',
         len(avg_lst), '.avg files', '\n',
         len(cnt_lst), '.cnt files', '\n',
         len(dat_lst), '.dat files', '\n',
         len(avg_ps_lst), '.ps files', '\n',
         len(orig_cnt_lst), 'orig.cnt files', '\n\n',
        '_____________________Missing File Extensions By Experiment_____________________', '\n')


    print('Missing avg files...')
    count=0
    for k,v in (avg_dict.items()):
        if k not in ns_avg_dict:
            count+=1
            print(count,")", k, 'is missing all avg files.')
        elif ns_avg_dict[k] != avg_dict[k]:
            diff = avg_dict[k] - ns_avg_dict[k]
            if diff == 1:
                count+=1
                print(count, ")", diff, k, 'file')
            else:
                print(count, ")", diff, k, 'files')

    if len(dat_lst) != 8:
        print('\n', 'Missing dat files =', ','.join(set(dat_names).difference(dat_lst)), '\n')
    if len(cnt_lst) != 10:
        print('Missing cnt files =', ','.join(set(cnt_names).difference(cnt_lst)), '\n')
    if len(avg_ps_lst) != 25:
        print('Missing ps files =', ','.join(set(ps_names).difference(avg_ps_lst)), '\n')

    if len(dat_lst) + len(cnt_lst) + len(avg_ps_lst) == 26:
        print('All dat/cnt/avg.ps files accounted for')


    print('_____________________Miscellaneous Extensions_____________________')    
    if len(h1_ps_lst) > 0:
        print(len(h1_ps_lst), 'h1.ps files found', '\n')
    if len(cnt_h1_lst) > 0:
        print(len(cnt_h1_lst), 'cnt.h1 files found', '\n')
    if len(avg_h1_lst) > 0:
        print(len(avg_h1_lst), 'avg.h1 files found', '\n')
    if len(ev2_lst) > 0:
        print(len(ev2_lst), 'ev2 files found', '\n')
    if len(cnt_rr_lst) > 0:
        print(len(cnt_rr_lst), 'cnt_rr files found', '\n')
    if len(bad_orig_lst) >0:
        print(len(bad_orig_lst), 'mislabeled orig files found', '\n')

    if len(h1_ps_lst) + len(cnt_h1_lst) + len(avg_h1_lst) + len(ev2_lst) + len(cnt_rr_lst) == 0:
        print('No h1.ps/cnt.h1/avg.h1/ev2/cnt_rr files found')

    if len(avg_lst) + len(avg_ps_lst) +  len(dat_lst) + len(cnt_lst) + len(orig_cnt_lst) == total_file_count + other_file_count - other_file_count:
        print('File counts check out')
    else:
        print('File count incorrect: check number of extensions')

    if other_file_count > 3:
        print('Check .sub/txt/db files')


def run_letter_check(fp):
    '''Given a file path, checks to see if each extension has same sub ID, 
    then checks if all run letters are the same'''

    dat_names = ('vp3', 'cpt', 'ern', 'ant', 'aod', 'ans', 'stp', 'gng')
    cnt_names = ('eeo', 'eec', 'vp3', 'cpt', 'ern', 'ant', 'aod', 'ans', 'stp', 'gng')
    ps_names = ('vp3', 'cpt', 'ern', 'ant', 'aod', 'anr', 'stp', 'gng')
    avg_dict = {'vp3': 3,
                'gng': 2,
                'ern': 4,
                'stp': 2,
                'ant': 4,
                'cpt': 6,
                'aod': 2,
                'anr': 2}

    print('You are in', fp,'\n')
    fp_splitter = fp.split('/')[-2:]
    two_levels = "/".join(fp_splitter)

    #use tuples from erp_extensions_check function to create lists of exps by extension 
    avg_run_count = [fname.split("_")[2] for fname in os.listdir(fp) if fname.endswith("avg") and fname.startswith(ps_names)]
    avg_ps_run_count = [fname.split("_")[2] for fname in os.listdir(fp) if fname.endswith("avg.ps") and fname.startswith(ps_names)]
    h1_ps_run_count = [fname.split("_")[2] for fname in os.listdir(fp) if fname.endswith("h1.ps") and fname.startswith(dat_names)]
    dat_run_count = [fname.split("_")[2] for fname in os.listdir(fp) if fname.endswith("dat") and fname.startswith(dat_names)]
    avg_h1_run_count = [fname.split("_")[2] for fname in os.listdir(fp) if fname.endswith("_avg.h1") and fname.startswith(dat_names)]
    cnt_rr_run_count = [fname.split("_")[2] for fname in os.listdir(fp) if fname.endswith("_rr.cnt") and fname.startswith(cnt_names)]
    cnt_run_count = [fname.split("_")[2] for fname in os.listdir(fp) if fname.endswith("_32.cnt") and fname.startswith(cnt_names)]
    cnt_h1_run_count = [fname.split("_")[2] for fname in os.listdir(fp) if fname.endswith("cnt.h1") and fname.startswith(cnt_names)]
    orig_cnt_run_count = [fname.split("_")[2] for fname in os.listdir(fp) if fname.endswith("_orig.cnt") and fname.startswith(cnt_names)]

    #sub id is the key and file extension is the value 
    ids_dict = {}
    for file in os.listdir(fp):
        if not file.endswith(('txt', 'sub', 'db')):
            split_fname = re.split(r'[_.A-Z]', file )
            ids_dict.setdefault(split_fname[3], []).append(split_fname[-1])


    print('____________________________________Are Sub IDs Identical?', '____________________________________', '\n')        

    #if there is more than 1 ID for each extension then error was made       
    for k,v in ids_dict.items():
        if len(ids_dict) != 1:
            print('ERROR: One of these IDs is wrong', k, set(ids_dict[k]), '\n')
        else:
            print('All IDs are the same', '\n')

    print('____________________________________Are Run Letters Identical?', '____________________________________' '\n')

    #most common files 
    if len(avg_run_count) != 0:
        print("here are the run letters for the", len(avg_run_count), ".avg files in", two_levels, "--", set(avg_run_count))
    if len(avg_ps_run_count) != 0:
        print("here are the run letters for the", len(avg_ps_run_count), ".ps files in", two_levels, "--", set(avg_ps_run_count))
    if len(cnt_run_count) != 0:
        print("here are the run letters for the", len(cnt_run_count), ".cnt files in", two_levels, "--", set(cnt_run_count))
    if len(dat_run_count) != 0:
        print("here are the run letters for the", len(dat_run_count), ".dat files in", two_levels, "--", set(dat_run_count))

    #not so common files     
    if len(cnt_rr_run_count) != 0:
        print("here are the run letters for the", len(cnt_rr_run_count), ".cnt_rr files in", two_levels, "--", set(cnt_rr_run_count))
    if len(h1_ps_run_count) != 0:
        print("here are the run letters for the", len(h1_ps_run_count), "avg.h1.ps files in", two_levels, "--", set(h1_ps_run_count))
    if len(cnt_h1_run_count) != 0:
        print("here are the run letters for the", len(cnt_h1_run_count), "cnt.h1.ps files in", two_levels, "--", set(cnt_h1_run_count))
    if len(orig_cnt_run_count) != 0:
        print("here are the run letters for the", len(orig_cnt_run_count), "_orig.cnt files in", two_levels, "--", set(orig_cnt_run_count))
    if len(avg_h1_run_count) != 0:
        print("here are the run letters for the", len(avg_h1_run_count), "avg.h1 files in", two_levels, "--", set(avg_h1_run_count))

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

def create_cnth1(lst_of_paths, set_of_exps):
    '''Given a path and experiment names -- will create cnt.h1 files and notify if any missing files'''
    
    erp_tasks = {'vp3', 'cpt', 'ern', 'ant', 'aod', 'ans', 'stp', 'gng'}
    tobe_converted = set_of_exps & erp_tasks
    tasks_tuple = tuple(tobe_converted)
    
    
    print('\n', '_________________________________________________CREATING CNT.H1S_________________________________________________')
    count = 0
    for roots, dirs, files in os.walk(lst_of_paths):
        for name in files:
            if name.startswith(tasks_tuple) and name.endswith('_32.cnt'):
                subprocess.call("create_cnthdf1_from_cntneuroX.sh {}".format(name), shell=True, cwd=lst_of_paths)
                print("creating new cnt.h1 from... " + name, '\n')
                count += 1 
            elif name.endswith("_rr.cnt"):
                print('\n', '!!!!!!!', "there's a re-run in", lst_of_paths.split('/')[-1], name, '!!!!!!!', '\n')
    
    if count != len(tasks_tuple):
        print('!!!!!!!', 'There was an experiment not found for', os.path.basename(lst_of_paths), '!!!!!!!!')
            
                
def create_ps(lst_of_paths):
    '''Given a path -- will create avg.h1,ps files'''
    print('\n', '_________________________________________________CREATE H1.PS_________________________________________________')            

    for path, subdirs, files in os.walk(lst_of_paths):
        for name in files:
            if name.endswith("avg.h1"):
                subprocess.call("plot_hdf1_data.sh {}".format(name), shell=True, cwd=lst_of_paths)
                print("creating ps files.. " + name)


def erp_exp_choice_child(lst_of_paths, set_of_exps):
    '''src=path of cnt files
    set_of_exps = tasks to convert written as a set with curly braces
    creates ps files and deletes cnt.h1 & avg.h1 of user defined number of exps'''
    
    #copy cnts and if re-run then flag it for proper processing 
    copy_cnts(lst_of_paths, set_of_exps)

    print('\n', '_________________________________________________CREATING AVG.H1_________________________________________________')

    for roots, dirs, files in os.walk(lst_of_paths):
        for name in files:
            if name.startswith(('vp3', 'cpt', 'ern', 'aod', 'stp', 'gng')) and name.endswith("_cnt.h1"):
                subprocess.call('create_avghdf1_from_cnthdf1X -lpfilter 16 -hpfilter 0.03 -thresh 100 -baseline_times -125 0 vp3*_cnt.h1 cpt*_cnt.h1 ern*_cnt.h1 aod*_cnt.h1 stp*_cnt.h1 gng*_cnt.h1', shell=True, cwd=lst_of_paths)
                print('converting', name)
            elif name.startswith('ant') and name.endswith("_cnt.h1"):
                subprocess.call('create_avghdf1_from_cnthdf1X -lpfilter 8 -hpfilter 0.03 -thresh 100 -baseline_times -125 0 ant*_cnt.h1', shell=True, cwd=lst_of_paths)
                print('converting', name)
            elif name.startswith('ans') and name.endswith("_cnt.h1"):
                subprocess.call('create_avghdf1_from_cnthdf1X -lpfilter 16 -hpfilter 0.03 -thresh 100 -baseline_times -125 0 ans*_cnt.h1', shell=True, cwd=lst_of_paths)
                print('converting', name) 
                
    #create ps files 
    create_ps(lst_of_paths)
    
    
def erp_exp_choice_adult(lst_of_paths, set_of_exps):
    '''src=path of cnt files
    set_of_exps = tasks to convert written as a set with curly braces
    creates ps files and deletes cnt.h1 & avg.h1 of user defined number of exps'''
    
    #copy cnts and if re-run then flag it for proper processing 
    copy_cnts(lst_of_paths, set_of_exps)

    print('\n', '_________________________________________________CREATING AVG.H1_________________________________________________')

    for roots, dirs, files in os.walk(lst_of_paths):
        for name in files:
            if name.startswith(('vp3', 'cpt', 'ern', 'aod', 'stp', 'gng')) and name.endswith("_cnt.h1"):
                subprocess.call('create_avghdf1_from_cnthdf1X -lpfilter 16 -hpfilter 0.03 -thresh 75 -baseline_times -125 0 vp3*_cnt.h1 cpt*_cnt.h1 ern*_cnt.h1 aod*_cnt.h1 stp*_cnt.h1 gng*_cnt.h1', shell=True, cwd=lst_of_paths)
                print('converting', name)
            elif name.startswith('ant') and name.endswith("_cnt.h1"):
                subprocess.call('create_avghdf1_from_cnthdf1X -lpfilter 8 -hpfilter 0.03 -thresh 75 -baseline_times -125 0 ant*_cnt.h1', shell=True, cwd=lst_of_paths)
                print('converting', name)
            elif name.startswith('ans') and name.endswith("_cnt.h1"):
                subprocess.call('create_avghdf1_from_cnthdf1X -lpfilter 16 -hpfilter 0.03 -thresh 100 -baseline_times -125 0 ans*_cnt.h1', shell=True, cwd=lst_of_paths)
                print('converting', name) 
                
    #create ps files 
    create_ps(lst_of_paths)         

                    
def erp_cnt_to_h1(dir_stem, exp_names, src):
    """Search a ns folder for cnt files of tasks used for peak picking, copies cnts to folders named after tasks, converts to avg.h1
    dir_stem = full path of where you want .avg.h1 files
    exp_names = list of experiment names
    src = full path of ns folder"""

    print('_________________________________________________CREATING NEW DIRECTORIES________________________________________________')

    #create directories based on experiment names
    for exp in exp_names:
        new_dirs = os.path.join(dir_stem, exp)
        if not os.path.exists(new_dirs):
            os.makedirs(new_dirs)
            print("creating " + new_dirs)
        else:
            print(new_dirs + " already there")


    print('\n', '_________________________________________________COPYING CNTS_________________________________________________')

    count11=0
    count22=0
    count33=0
    for roots, dirs, files in os.walk(src):
        for name in files:
            if name.endswith("_orig.cnt"):
                pass
            if name.startswith(exp_names[0]) and name.endswith(("_32.cnt", "_rr.cnt")):
                shutil.copy(os.path.abspath(roots + '/' + name), os.path.join(dir_stem, exp_names[0]))
                count11+=1
                print("Copying...", name)
            elif name.startswith(exp_names[1]) and name.endswith(("_32.cnt", "_rr.cnt")):
                shutil.copy(os.path.abspath(roots + '/' + name), os.path.join(dir_stem, exp_names[1]))
                count22+=1
                print("Copying...", name)
            elif name.startswith(exp_names[2]) and name.endswith(("_32.cnt", "_rr.cnt")):
                shutil.copy(os.path.abspath(roots + '/' + name), os.path.join(dir_stem, exp_names[2]))
                count33+=1
                print("Copying...", name)

    print('\n', count11, exp_names[0], 'cnt files', '\n',
           count22, exp_names[1], 'cnt files', '\n',
           count33, exp_names[2], 'cnt files', '\n')

    print('\n', '_________________________________________________FIXING RERUNS_________________________________________________')


    #fixes file formatting in re run and lets user know if rerun has 1 as run number
    for root, dirs, files in os.walk(dir_stem):
        for name in files:
            if name.endswith("_rr.cnt"):
                split = name.split("_")[2][1] #this is the run number 
                if split == '2':
                    os.rename(os.path.join(root, name), os.path.join(root,name.replace("_rr", "")))
                    print('\n', 'Renaming', os.path.join(root,name), '\n', 
                          'to','\n', os.path.join(root,name.replace("_rr", ""), '\n'))
                elif split == '1':
                    os.remove(os.path.join(root, name))
                    print('Run number error in', name, '...', 'Removing from new directory...')
            else:
                print(name, "not a rerun")
    print('\n', '_________________________________________________CREATING CNT.H1S_________________________________________________')

    #create cnt.h1
    for path, subdirs, files in os.walk(dir_stem):
        for name in files:
            if name.endswith(".cnt"):
                subprocess.call("create_cnthdf1_from_cntneuroX.sh {}".format(name), shell=True, cwd=path)
                print("creating new cnt.h1 from... " + name)

    print('\n', '_________________________________________________CREATING AVG.H1S_________________________________________________')

    #this works but loops too many times--need to fix 
    for path, subdirs, files in os.walk(dir_stem):
        for name in files:    
            if name.startswith("ant") and name.endswith("_cnt.h1"):
                os.chdir(os.path.join(path))
                subprocess.call("create_avghdf1_from_cnthdf1X -lpfilter 8 -hpfilter 0.03 -thresh 75 -baseline_times -125 0 *_cnt.h1", shell=True)
                print("creating avg.h1 from " + name)
            elif name.startswith(("aod", "vp3")) and name.endswith("_cnt.h1"):
                os.chdir(os.path.join(path))
                subprocess.call("create_avghdf1_from_cnthdf1X -lpfilter 16 -hpfilter 0.03 -thresh 75 -baseline_times -125 0 *_cnt.h1", shell=True)
                print("creating avg.h1 from " +name)

    print('\n', '_________________________________________________CLEANUP_________________________________________________')

    #remove unecessary files 
    for path, subdirs, files in os.walk(dir_stem):
        for name in files:
            if name.endswith((".cnt", "_cnt.h1")):
                os.remove(os.path.join(path + '/' + name))
                print("removing... " + name)

    return True



def erp_peak_mover(base_dir, hbnl_ant, hbnl_ant_rej, 
                  hbnl_aod, hbnl_aod_rej, 
                  hbnl_vp3, hbnl_vp3_rej):
    '''given the reject/non reject for ant, aod, vp3 experiments, this will copy those
    files to the correct directory.  base_dir is the subdir containing the
    aod/ant/vp3 files'''


    if os.path.isdir(base_dir):
        pass
    else:
        print('Path does not exist, check -->', base_dir)
        sys.exit()

    if os.path.isdir(hbnl_ant):
        pass
    else:
        print('Path does not exist, check -->', hbnl_ant)
        sys.exit()

    if os.path.isdir(hbnl_ant_rej):
        pass
    else:
        print('Path does not exist, check -->', hbnl_ant_rej)
        sys.exit()

    if os.path.isdir(hbnl_aod):
        pass
    else:
        print('Path does not exist, check -->', hbnl_aod)
        sys.exit()

    if os.path.isdir(hbnl_aod_rej):
        pass
    else:
        print('Path does not exist, check -->', hbnl_aod_rej)
        sys.exit()

    if os.path.isdir(hbnl_vp3):
        pass
    else:
        print('Path does not exist, check -->', hbnl_vp3)
        sys.exit()

    if os.path.isdir(hbnl_vp3_rej):
        pass
    else:
        print('Path does not exist, check -->', hbnl_vp3_rej)
        sys.exit()

    #create dictionaries for each experiment 
    vp3d={}
    aodd = {}
    antd={}
    vp3_path = os.path.join(base_dir, 'vp3')
    ant_path = os.path.join(base_dir, 'ant')
    aod_path = os.path.join(base_dir, 'aod')
    for root, dirs, files in os.walk(base_dir):
        for name in files:
            if name.startswith('vp3'):
                vp3_split = name.split('_')
                vp3d.setdefault(vp3_split[3], []).append(vp3_split[4])
            if name.startswith('ant'):
                ant_split = name.split('_')
                antd.setdefault(ant_split[3], []).append(ant_split[4])
            if name.startswith('aod'):
                aod_split = name.split('_')
                aodd.setdefault(aod_split[3], []).append(aod_split[4])

    #response lists
    yes = ['yes', 'y', 'YES', 'Y']
    no = ['no', 'n', 'NO', 'N']  

    #VP3 
    vp3_count_remove = 0
    vp3_count_keep = 0
    print('VP3 FILES TO BE MOVED', '\n')           
    for k,v in vp3d.items():
        if 'avg.mt' not in vp3d[k]:
            vp3_count_remove +=1
            vp3_rej = '*' + k + '*'
            print('\n', k,v)
            answer=input('Move to REJECTS folder? ')
            for name in glob(os.path.join(vp3_path, vp3_rej)):
                if answer in yes:
                    shutil.copy(os.path.join(vp3_path, name), hbnl_vp3_rej)
                if answer in no:
                    pass
        elif 'avg.mt' in vp3d[k]:
            vp3_count_keep+=1
            vp3_keep='*' + k + '*'
            print('\n', k,v)
            answer=input('Move to NON REJECTS folder? ')
            for name in glob(os.path.join(vp3_path, vp3_keep)):
                if answer in yes:
                    shutil.copy(os.path.join(vp3_path, name), hbnl_vp3)
                if answer in no:
                    pass


    print('\n', vp3_count_keep, 'subs accepted',
         '\n', vp3_count_remove, 'subs rejected', '\n\n\n')

    #ANT
    ant_count_remove = 0
    ant_count_keep = 0
    print('ANT FILES TO BE MOVED', '\n')           
    for k,v in antd.items():
        if 'avg.mt' not in antd[k]:
            ant_count_remove +=1
            ant_rej = '*' + k + '*'
            print('\n', k,v)
            answer=input('Move to REJECTS folder? ')
            for name in glob(os.path.join(ant_path, ant_rej)):
                if answer in yes:
                    shutil.copy(os.path.join(ant_path, name), hbnl_ant_rej)
                if answer in no:
                    pass
        elif 'avg.mt' in antd[k]:
            ant_count_keep+=1
            ant_keep='*' + k + '*'
            print('\n', k,v)
            answer=input('Move to NON REJECTS folder? ')
            for name in glob(os.path.join(ant_path, ant_keep)):
                if answer in yes:
                    shutil.copy(os.path.join(ant_path, name), hbnl_ant)
                if answer in no:
                    pass


    print('\n', ant_count_keep, 'subs accepted',
         '\n', ant_count_remove, 'subs rejected', '\n\n\n')

    #AOD
    aod_count_remove = 0
    aod_count_keep = 0
    print('AOD FILES TO BE MOVED', '\n')           
    for k,v in aodd.items():
        if 'avg.mt' not in aodd[k]:
            aod_count_remove +=1
            aod_rej = '*' + k + '*'
            print('\n', k,v)
            answer=input('Move to REJECTS folder? ')
            for name in glob(os.path.join(aod_path, aod_rej)):
                if answer in yes:
                    shutil.copy(os.path.join(aod_path, name), hbnl_aod_rej)
                if answer in no:
                    pass
        elif 'avg.mt' in aodd[k]:
            aod_count_keep+=1
            aod_keep='*' + k + '*'
            print('\n', k,v)
            answer=input('Move to NON REJECTS folder? ')
            for name in glob(os.path.join(aod_path, aod_keep)):
                if answer in yes:
                    shutil.copy(os.path.join(aod_path, name), hbnl_aod)
                if answer in no:
                    pass


    print('\n', aod_count_keep, 'subs accepted',
         '\n', aod_count_remove, 'subs rejected', '\n\n\n')
    return True