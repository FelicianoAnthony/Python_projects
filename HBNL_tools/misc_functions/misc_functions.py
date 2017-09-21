import os
import shutil
import sys
import pandas as pd
import operator



def batch_change_runletter(path, bad_letter, good_letter):
	""" change run letter ONLY for all neuropsych files in directory 
       ex: 2032345364_CBST_1_g3.txt >> 2032345364_CBST_1_h3.txt """

    for r,d,f in os.walk(path):
        for n in f:
            if n.endswith(('sub', 'db')):
                pass
            else:
                if n.split('_')[2][0] == bad_letter:
                    new_fname = n.replace('_' + bad_letter, good_letter)
                    os.rename(os.path.join(r,n), os.path.join(r, new_fname))
                    print('changed')


def rename_extension(path, bad_name_str, new_name_str):
    """ change original.cnt to orig.cnt """

    for r,d,f in os.walk(path):
        for n in f:
            if bad_name_str in n:
                new_fname = n.replace(bad_name_str, new_name_str)
                os.rename(os.path.join(r,n), os.path.join(r, new_fname))
                print('changed')


def tracker_by_site(filepath, neuro_or_erp):
    """ given a file that contains ALL tracker files for neuro or ERP in a certain month -- will
    separate into .txt files based on site number & sort by date """


    dirname = os.path.dirname(tracker_path)
    with open(filepath,'r') as f:
        entries = map(str.strip,f.readlines())

    entries = sorted([entry.split() for entry in entries], key = lambda k: k[2])

    for entry in entries:
        ID = entry[1][0]
        with open(os.path.join(dirname, neuro_or_erp).format(ID),'a') as f:
            f.write(' '.join(entry) + '\n')
    return True


def rename_sub_ids(path, good_id_str, bad_id_str):
    '''renames sub ID for ERP data'''

    for r,d,f in os.walk(p):
        for n in f:
            if bad_id_str in n:
                new_name = n.replace(bad_id_str, good_id_str)
                print('Renaming to ', os.path.join(r,new_name))
                os.rename(os.path.join(r,n), os.path.join(r,new_name))

def sync_error(ev2_path, dat_path):
    """ Provide **FULL** file pathway of event file and dat file and function will return corrected event file.
       If ev2 file is missing an entire event then program will stop as data is corrupted """


    df = pd.read_csv(ev2_path, header=None, delim_whitespace=True)
    df.columns = ['trial','type','stim1', 'stim2', 'stim3', 'latency']


    non_zero_ev2= df.loc[df['type'] > 0]
    zero_ev2= df.loc[df['type'] < 0.9] 
    non_zero_ev2.sort('trial', ascending=True, inplace=True) 


    lst = []
    with open(dat_path, 'r') as f:
        for line in f.readlines()[21:]:
            lst.append(line.split())
            df_dat = pd.DataFrame(lst)
            df_dat.columns=['trial','resp','type', 'correct', 'latency', 'stim']


    if len(non_zero_ev2) != len(df_dat):
        print('ev2 file is', len(non_zero_ev2), 'lines long', '\n', 
              'dat file is', len(df_dat), 'lines long', '\n',
              'dat file is', len(df_dat) - len(non_zero_ev2), 'line longer than event file')
        sys.exit()

    non_zero_ev2['type'] = df_dat['type'].values

    frames = [zero_ev2, non_zero_ev2]
    new_ev2_df = pd.concat(frames)
    new_ev2_df.to_csv(ev2_path ,sep = " ", index=False, header=False)

    return True


def sloreta_parser(fname, fpath):

    ''' maps output of SLORETA statistics to Brodmann Area '''
    
    base_path = os.path.dirname(fpath)
    new_path = os.path.join(base_path, fname)

    print(fpath, '\n')
    df = pd.read_csv(fpath)
    df1 = df.reset_index()
    df1.columns = df1.columns.str.strip()
    structure_df = df1['Structure'].str.strip()
    bman_df= df1['Brodmann area'].values

    df_tup = collections.Counter(zip(bman_df, structure_df)).most_common()

    brod_num, sig_vox = zip(*df_tup)
    df_tup.sort(key=operator.itemgetter(1), reverse=True)

    my = open(new_path, 'w')
    for i in sorted(df_tup, key=lambda x:x[0][0]):
        if i[1] == 1:
            z = 'There is', i[1], 'significant voxel in', i[0][1], 'Area', i[0][0]
            my.write(str(z).replace(',', '').replace("'", ''). replace("(", '').replace(")", '') + '\n')
        else:
            z = 'There are', i[1], 'significant voxels in', i[0][1], 'Area', i[0][0]
            my.write(str(z).replace(',', '').replace("'", ''). replace("(", '').replace(")", '') + '\n')
    my.close()


def amp_thresh_check(fp, electrode_names, uv_threshold):
    ''' checks avg.h1 files (416 x 61 martix) for any values above uv_threshold '''
    
    #store electrode names in variable 
    with open(electrode_names, 'rt') as file:
        csv_file =csv.reader(file,delimiter=',')
        for i in csv_file:
            channel_lst = i

    #read txt files and use electrode names as columns           
    df = pd.read_csv(fp, sep= '\s+', header = None)
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