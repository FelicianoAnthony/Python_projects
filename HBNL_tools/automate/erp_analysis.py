import os
import sys
from glob import glob
from collections import defaultdict
from collections import Counter
import collections
import re
import shutil
import subprocess
import pandas as pd

class site_data:
    #get_h1s()
    def __init__(self):
    
        self.ant_set = {'ant'}
        self.ans_set = {'ans'}
        self.other_exps = {'vp3', 'cpt', 'ern', 'aod', 'stp', 'gng'}
        
    #get_h1s()    
    def check_cnt_copy(self, fp_check_cnt):
        '''create dictionary of lists where id is key and exp*cnt names are the values'''
    
        self.fp_check_cnt = fp_check_cnt

        cnt_dict = {}
        for r,d,f in os.walk(fp_check_cnt):
            for n in f:
                if n.endswith('_32.cnt'):
                    split = n.split('_')
                    cnt_dict.setdefault(split[3], []).append(split[0])
                    
        for k,v in cnt_dict.items():
            if len(v) is not 3:
                print('Check {} for experiments {}'.format(k,v))
    #get_h1s()                
    def rename_reruns(self, fp_rerun, fp_rerun_trg=None):
        '''if peak-picking, copy rr file to target directory and rename it.
           if not peak-picking, only let me know there is a rr file'''

        self.fp_rerun = fp_rerun
        self.fp_rerun_trg = fp_rerun_trg
        
        #check for _rr.cnt regardless of run number 
        for r,d,f in os.walk(fp_rerun):
            for n in f:
                if n.endswith('_rr.cnt'):
                    print('Found re-runs...',  os.path.basename(fp_rerun), n)
                    answer=input('Copy to target directory?')
                    if answer in ['y', 'Y', 'yes', 'Yes']:
                        shutil.copy(os.path.join(r,n), os.path.join(fp_rerun_trg, n[:3])) 
                    else:
                        pass
                    
        #rename only if peak picking              
        if fp_rerun_trg:
            for r,d,f in os.walk(fp_rerun_trg):
                for n in f:
                    if n.endswith('_rr.cnt'):
                        new_name = os.rename(os.path.join(r, n), os.path.join(r,n.replace("_rr", "")))
                        print('\n', 'Renaming', os.path.join(r,n), '\n', 
                              'to','\n', os.path.join(r,n.replace("_rr", ""), '\n'))
    #get_h1s()                    
    def create_cnth1(self, fp_cnt):
        '''given a filepath -- create _cnt.h1 files from shell script'''
        
        self.fp_cnt = fp_cnt
        
        print('\n', '_________________________________________________CREATING CNT.H1S_________________________________________________')
        for r,d,f in os.walk(fp_cnt):
            for n in f:
                if n.startswith(self.cnth1_tups) and n.endswith('_32.cnt'):
                    path = os.path.join(r,n)
                    p = subprocess.Popen("create_cnthdf1_from_cntneuroX.sh {}".format(path),shell=True, 
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.path.dirname(path))
                    result = p.communicate()[1]
                    print(result.decode('ascii'))

    #get_h1s()
    def create_avgh1(self, fp_h1):
        '''given a filepath -- create _avg.h1 files from shell script'''
        
        self.fp_h1 = fp_h1

        print('\n', '_________________________________________________CREATING AVG.H1_________________________________________________')            
        for r,d,f in os.walk(fp_h1):
            for n in f:
                if n.startswith(self.ant_tup) and n.endswith('cnt.h1'):
                    ant_path = os.path.join(r,n)
                    p_ant = subprocess.Popen('create_avghdf1_from_cnthdf1X -lpfilter 8 -hpfilter 0.03 -thresh 75 -baseline_times -125 0 {}'.format(ant_path), 
                                             shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.path.dirname(ant_path))
                    result_ant = p_ant.communicate()[1]
                    print(result_ant.decode('ascii'))
                if n.startswith(self.ans_tup) and n.endswith('cnt.h1'):
                    ans_path = os.path.join(r,n)
                    p_ans = subprocess.Popen('create_avghdf1_from_cnthdf1X -lpfilter 16 -hpfilter 0.03 -thresh 100 -baseline_times -125 0 {}'.format(ans_path), 
                                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.path.dirname(ans_path))
                    result_ans = p_ans.communicate()[1]
                    print(result_ans.decode('ascii'))
                if n.startswith((self.others_tup)) and n.endswith('cnt.h1'):
                    path=os.path.join(r,n)
                    p_others = subprocess.Popen('create_avghdf1_from_cnthdf1X -lpfilter 16 -hpfilter 0.03 -thresh 75 -baseline_times -125 0 {}'.format(path), 
                                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.path.dirname(path))
                    result_others = p_others.communicate()[1]
                    print(result_others.decode('ascii'))
    #get_h1s()
    def create_avgps(self, fp_ps):
        '''given a filepath -- create avg.h1.ps files from shell script'''
        
        self.fp_ps = fp_ps

        print('\n', '_________________________________________________CREATE H1.PS_________________________________________________')
        for path, subdirs, files in os.walk(fp_ps):
            for name in files:
                if name.endswith("avg.h1"):
                    ps_paths = os.path.join(path, name)
                    subprocess.Popen("plot_hdf1_data.sh {}".format(name), shell=True, cwd=os.path.dirname(ps_paths))
                    print("creating ps files.. " + name)
                    
    #get_h1s()                
    def delete_bad_files(self, fp_to_delete, to_be_deleted_set):
        '''given a filepath -- deletes extensions found in both del_set & to_be_delete_set
           {to_be_deleted_set}'''
    
        self.fp_to_delete = fp_to_delete
        self.to_be_deleted_set = to_be_deleted_set

        del_set = {'_32.cnt', 'cnt.h1', 'avg.h1', 'avg.h1.ps'}
        del_files = del_set & to_be_deleted_set
        del_tup = tuple(del_files)
        print('\n', '_________________________________________________CLEANING UP...________________________________________________')
        
        for r,d,f in os.walk(fp_to_delete):
            for n in f:
                if n.endswith(del_tup):
                    path = os.path.join(r,n)
                    os.remove(path)
                    print('removing...', n)
                    
    #erp_peak_mover()
    def dir_exist(self, dir_path):
        '''checks if path exists and exits program if it does not'''
        
        self.dir_path = dir_path
        
        if os.path.isdir(dir_path):
            pass
        else:
            print('Path does not exist, check -->', dir_path)
            sys.exit(1)
            
    #erp_peak_mover()
    def concat_peak_paths(self, hbnl_dir, site):
        '''concats path to peak picked and reject directory for any site'''
        
        self.hbnl_dir = hbnl_dir
        self.site = site

        peak_pick_dirs = ['ant_phase4__peaks_2017', 'aod_phase4__peaks_2017', 'vp3_phase4__peaks_2017']
        hbnl = '/vol01/active_projects/HBNL/'

        good_dirs = [hbnl + '/' + i + '/' + site for i in peak_pick_dirs]
        rej_dirs = [hbnl + '/' + i + '/' + site + '/' + 'reject' for i in peak_pick_dirs]

        return good_dirs, rej_dirs

    #erp_peak_mover()
    def peak_pick_move(self, source_path, exp_to_move, 
                       dict_of_lists, good_dir, rej_dir):
        '''creates a dictionary of ids & extensions associated with that id.
           eventually moves these files to directory created in concat_peaks_path.
           requires user input.'''
        
        self.source_path = source_path
        self.exp_to_move = exp_to_move
        self.dict_of_lists = dict_of_lists
        self.good_dir = good_dir
        self.rej_dir = rej_dir

        yes = ['yes', 'y', 'YES', 'Y']
        no = ['no', 'n', 'NO', 'N']  
        concat_exp_path = os.path.join(source_path, exp_to_move)

        count_remove = 0
        count_keep = 0
        print(exp_to_move, 'FILES TO BE MOVED', '\n')           
        for k,v in dict_of_lists.items():
            if 'avg.mt' not in v:
                count_remove +=1
                rej = '*' + k + '*'
                print('\n', k,v)
                wildcard_path_rej = os.path.join(concat_exp_path, rej)
                for name in glob(wildcard_path_rej): #/active_projects/anthony/peaks_dir/ant/*40360200*
                    answer=input('Move to REJECTS folder?\n\n')
                    if answer in yes:
                        shutil.copy(os.path.join(wildcard_path_rej, name), rej_dir)
                    if answer in no:
                        pass
            if 'avg.mt' in v:
                count_keep +=1
                keep = '*' + k + '*'
                print('\n', k,v)
                wildcard_path = os.path.join(concat_exp_path, keep)
                for name in glob(wildcard_path): #/active_projects/anthony/peaks_dir/ant/*40360200* 
                    answer=input('Move to NON-REJECTS folder?\n\n')
                    if answer in yes:
                        shutil.copy(os.path.join(wildcard_path, name), good_dir)
                    if answer in no:
                        pass

        print('\n', count_keep, 'subs accepted',
         '\n', count_remove, 'subs rejected', '\n\n\n')
    
    def get_h1s(self, fp, set_of_exps, del_ext={}, ps=None, trg_dir=None):
        '''combines all these commands together'''
        
        self.fp = fp
        self.set_of_exps = set_of_exps
        self.del_ext = del_ext
        self.ps = ps
        self.trg_dir = trg_dir
        
        #use in create_cnth1()
        self.cnth1_tups = tuple(set_of_exps)
        
        if_ant = self.ant_set & set_of_exps
        if_ans = self.ans_set & set_of_exps
        all_others = self.other_exps & set_of_exps
        
        #used in create_avgh1()
        self.ant_tup = tuple(if_ant)
        self.ans_tup = tuple(if_ans)
        self.others_tup = tuple(all_others)

        #if being used for peak picking, create new directories and move all cnt files to the correct folder...and so on
        if trg_dir:
            #create new directories
            exps_list = list(set_of_exps)
            for exp in exps_list:
                new_dirs = os.path.join(trg_dir, exp)
                if not os.path.exists(new_dirs):
                    os.makedirs(new_dirs)
                    print("Creating " + new_dirs)
                else:
                    print(new_dirs + " already exist")
            #copy cnt files to newly created directories       
            count = 0
            for r,d,f in os.walk(fp):
                for n in f:
                    if n.startswith(self.cnth1_tups) and n.endswith('_32.cnt'):
                        count+=1
                        print('Copying ', n)
                        shutil.copy(os.path.join(r,n), os.path.join(trg_dir, n[:3]))
            print('Copied', count, 'files')
                        
            self.rename_reruns(fp,fp_rerun_trg=trg_dir)
            self.check_cnt_copy(trg_dir)
            self.create_cnth1(trg_dir)
            self.create_avgh1(trg_dir)
            if ps:
                self.create_avgps(trg_dir)
            if del_ext:
                self.delete_bad_files(trg_dir, del_ext)
            return True
        
        #if you want to create avg.h1s IN directory copying files...
        self.rename_reruns(fp)
        self.create_cnth1(fp)
        self.create_avgh1(fp)
        if ps:
            self.create_avgps(fp)
        if del_ext:
            self.delete_bad_files(fp, del_ext)
            
    def erp_peak_mover(self, base_dir, site):
        '''given the parent directory of peak picked files, 
           moves files to peak picked or reject directory.'''
        
        self.base_dir = base_dir
        self.site = site
    
        #create paths to accepted and rejected folders based on site
        tup = self.concat_peak_paths(base_dir, site)
        ant_good = tup[0][0]
        aod_good = tup[0][1]
        vp3_good = tup[0][2]

        ant_rej = tup[1][0]
        aod_rej = tup[1][1]
        vp3_rej = tup[1][2]

        #check if those directories exist
        base_dir_exists = self.dir_exist(base_dir)

        ant_exists = self.dir_exist(ant_good)
        antrej_exists = self.dir_exist(ant_rej)
        aod_exists = self.dir_exist(aod_good)
        aodrej_exists = self.dir_exist(aod_rej)
        vp3_exists = self.dir_exist(vp3_good)
        vp3rej_exists = self.dir_exist(vp3_rej)

        #create dictioanry of id and extensions
        vp3d={}
        aodd = {}
        antd={}
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

        #move to correct directory            
        self.peak_pick_move(base_dir, 'ant', antd, ant_good, ant_rej)
        self.peak_pick_move(base_dir, 'aod', aodd, aod_good, aod_rej)
        self.peak_pick_move(base_dir, 'vp3', vp3d, vp3_good, vp3_rej)


    def print_h1_headers(self, file_path, set_of_exps, del_ext={}):
        '''given a filepath and set of experiments, 
           creates header files in same directory'''
        
        self.file_path = file_path
        self.set_of_exps = set_of_exps
        self.del_ext = del_ext

        all_exps_tup =('vp3', 'cpt', 'ern', 'ant', 'aod', 'ans', 'stp', 'gng')

        #call on previous function 
        self.get_h1s(file_path,set_of_exps,del_ext=del_ext)


        #search for avg.h1 files and create header files 
        for r,d,f in os.walk(file_path):
            for n in f:
                if n.endswith('avg.h1'):
                    path = os.path.join(r,n)
                    fname = '_'.join(os.path.basename(path).split('_')[:-1])
                    p = subprocess.Popen('print_h5_header {}'.format(path),shell=True,stdout=subprocess.PIPE, universal_newlines=True)
                    result = p.communicate()[0]
                    with open(os.path.dirname(path) +'/'+ fname + '.txt', 'w') as f:
                        for l in result:
                            f.write(l)

        #{sub_id:[path_to_stp_header.txt, path_to_vp3_header.txt...]}
        header_dict={}
        for r,d,f in os.walk(file_path):
            for n in f:
                if n.startswith((all_exps_tup)) and n.endswith('txt'):
                    header_paths = os.path.join(r,n)
                    sub_id = os.path.dirname(header_paths)
                    header_dict.setdefault(sub_id[-8:], []).append(header_paths)

        return header_dict 


    def parse_header_files(self, header_path):
        '''given the path to a header file,
           returns df of accepted/rejected button presses by stimuli condition'''
        
        self.header_path = header_path
        
        
        starting_point = []
        with open(header_path, 'r') as f:
            for idx,l in enumerate(f):
                slines = l.splitlines()
                for i in slines:
                    if 'trial 0' in i:
                        for i in slines:
                            starting_point.append(idx)

        start = int(str(starting_point).replace('[', '').replace(']', ''))

        trial_num = []
        response_id = []
        stim_id = []
        accepted = []
        case_num = []
        correct = []

        with open(header_path, 'r') as f:
            for l in f.readlines()[start:]: 
                slines= l.splitlines()
                for i in slines:
                    strip = i.strip()
                    if 'trial_num' in strip:
                        formatted_num = strip.replace(' ', '').replace('"', '').replace(',', '')
                        trial_num.append(formatted_num)
                    if 'response_id' in strip:
                        formatted_resp = strip.replace(' ', '').replace('"', '').replace(',', '')
                        response_id.append(formatted_resp)
                    if 'stim_id' in strip:
                        formatted_stim = strip.replace(' ', '').replace('"', '').replace(',', '')
                        stim_id.append(formatted_stim)
                    if 'accepted' in strip:
                        formatted_acc = strip.replace(' ', '').replace('"', '').replace(',', '')
                        accepted.append(formatted_acc)
                    if 'case_num' in strip:
                        formatted_case = strip.replace(' ', '').replace('"', '').replace(',', '')
                        case_num.append(formatted_case)
                    if 'correct' in strip:
                        formatted_correct = strip.replace(' ', '').replace('"', '').replace(',', '')
                        correct.append(formatted_correct)


        trial_num_num = [i[10:] for i in trial_num]
        response_id_id = [i[12:] for i in response_id]
        stim_id_id = [i[8:] for i in stim_id]
        accepted_acc = [i[9:] for i in accepted]
        case_num_num = [i[9:] for i in case_num]
        correct_cor = [i[8:] for i in correct]

        d3 = {}
        d3 ['trial_num'] = trial_num_num
        d3 ['response_id'] = response_id_id
        d3 ['stim_id'] = stim_id_id
        d3 ['accepted'] = accepted_acc
        d3 ['case_num'] = case_num_num
        d3 ['correct'] = correct_cor

        df = pd.DataFrame.from_dict(d3, orient='index').T

        grouped = df.groupby(['stim_id','case_num', 'accepted', 'correct'])
        grouped_df = pd.DataFrame(grouped.size())

        print(header_path, '\n\n')
        return grouped_df