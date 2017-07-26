from db import database as D
import db.compilation as C
import pandas as pd
import sys

#knowledge
neuropsych_variables = ['motivCBST', 'motivTOLT','mim_3b', 'mom_3b', 'em_3b', 'ao_3b', 'apt_3b', 'atoti_3b', 
                        'ttrti_3b', 'atrti_3b','mim_4b', 'mom_4b', 'em_4b', 'ao_4b', 'apt_4b', 'atoti_4b', 'ttrti_4b', 
                        'atrti_4b', 'mim_5b', 'mom_5b', 'em_5b', 'ao_5b', 'apt_5b', 'atoti_5b', 'ttrti_5b', 'atrti_5b',
                        'mim_tt', 'mom_tt', 'em_tt', 'ao_tt', 'apt_tt', 'atoti_tt', 'ttrti_tt', 'atrti_tt',
                        'otr_3b', 'otr_4b', 'otr_5b', 'otr_tt', 'tc_f', 'span_f', 'tcat_f', 'tat_f',
                        'tc_b', 'span_b', 'tcat_b', 'tat_b']

missing = ['id', 'dob', 'gender', 'hand', 'testdate', 'sessioncode']

#all neuropsych conditions & measures
neuro_knowledge = {'VST' : [('b', 'f', ['span', 'tcat', 'tat', 'tc'])],
                   'TOLT': [('3b', '4b', '5b', 'tt',['ao', 'apt', 'atoti', 'atrti', 'em', 
                                                    'mim', 'mom', 'otr', 'ttrti'])]}


#default projections
default_neuro_proj = {'ID': 1, 'np_session':1, 'gender': 1, 
                      'age': 1, 'hand' :1, 'testdate':1, '_id':0}

default_neuro_admin = {'ID':1, 'np_session':1, 'filepath': 1, 
                       '_id' : 1, 'insert_time': 1}

def remap_neuro_variables(neuro_var_names):
    
    '''creates a mapping between old neuropsych variable names and more intuitive way of
       representing variable names -- exp_condition_measure'''

    neuro_var_dict = {}
    for var in neuropsych_variables:
        split = var.split('_')
        if len(split) == 2:
            if len(split[1]) == 2:
                tolt = 'TOLT' + '_' + split[1] + '_' + split[0]
                neuro_var_dict[var] = tolt
            if len(split[1]) == 1:
                cbst = 'VST' + '_' + split[1] + '_' + split[0]
                neuro_var_dict[var] = cbst
        if len(split) == 1:
            motiv = split[0][0:5]
            name = split[0][5:]
            if 'TOLT' in name:
                new_tolt = name + '_' + motiv
                neuro_var_dict[var] = new_tolt
            if 'CBST' in name:
                name = 'VST'
                new_vst = name + '_' + motiv
                neuro_var_dict[var] = new_vst

    return neuro_var_dict


def rename_neuropsych_cols(df, neuro_variables_dict):
    '''replaces neuropsych variable names in data frame'''
    return df.rename(columns={k:v for k,v in neuro_variables_dict.items() if k in df.columns})


def arg_compatability(uids_lst=None, neuro_exp_only=None, neuro_dict=None):
    '''self-explanatory'''
    
    if neuro_dict and neuro_exp_only:
        print('ERROR: Neuro_exp_only would return ALL conditions & measures for that experiment.\n'
              'Neuro_dict will get specific conditions & measures for 1 experiment')
        sys.exit(1)


def arg_filter_check(knowledge_lst, user_generated_lst, error_msg):
    '''compares two lists to identify what's in one that isn't 
       in the other.  prints specific error messages.'''
    
    common_in_both = set(knowledge_lst) & set(user_generated_lst)
    if len(common_in_both) != len(user_generated_lst):
        missing = set(user_generated_lst) - set(knowledge_lst)
        print(error_msg, missing)
        sys.exit(1)


def check_args_against_knowledge(neuro_dict): 
    '''checks component parts of neuro_dict to make sure theyre in neuropsych knowledge dictionary'''

    # separate each element of dictionary 
    for k,v, in neuro_dict.items():
        for i in v:
            val_len = len(i) - 1 #will work since there there's always 1 list at end of value
            user_exp = [k]
            user_conds = list(i[0:val_len])
            user_measures = i[-1]

    all_exps = ['TOLT', 'VST']

    #format exp
    exp_str = str(user_exp)
    exp_formatted = exp_str.replace('[', '').replace(']', '').replace("'", "")

    #check for exps
    exp_err = 'ERROR: Name not found. Check capitalization/spelling for '
    arg_filter_check(all_exps, user_exp, exp_err)


    #check conditions 
    cp_err = 'ERROR: Name not found. Check capitalization/spelling for'
    meas_err = 'ERROR: Name not found. Check capitalization/spelling for '
    
    if 'VST' == exp_formatted:
        #for neuro knowledge list
        vst_cps = neuro_knowledge['VST']
        for i in vst_cps:
            val_len = len(i) - 1
            cp_lst_vst = list(i[0:val_len])
            meas_vst = i[-1]

        arg_filter_check(cp_lst_vst, user_conds, cp_err)
        arg_filter_check(meas_vst, user_measures, meas_err) 

    if 'TOLT' == exp_formatted:
        #for neuro knowledge list
        tolt_cps = neuro_knowledge['TOLT']
        for i in tolt_cps:
            val_len = len(i) - 1
            cp_lst_tolt = list(i[0:val_len])
            meas_tolt = i[-1]
            
            arg_filter_check(cp_lst_tolt, user_conds, cp_err)
            arg_filter_check(meas_tolt, user_measures, meas_err)


def strip_lst(variable):
    '''helper function for create_neuro_dict()'''
    
    format_var = str(list(variable))
    new_var =  format_var.replace('[', '').replace(']', '').replace("'", "")
    return new_var
    

def create_neuro_dict(exp_str, conds_lst, measures_lst):
    '''given these args & type specified, returns a formatted neuropsych dictionary'''

    neuropsych_dict = {}
    
    vals = conds_lst, measures_lst
    neuropsych_dict[exp_str] = [vals]

    for k,v in neuropsych_dict.items():
        for idx, tpl in enumerate(v):
            val = strip_lst(tpl[0][0]), strip_lst(tpl[0][1]), tpl[1]
            v[idx] = val
            
    return neuropsych_dict


def neuro_dict_proj(neuro_dict):
    
    '''created projections from user created dictionary.
   contains function that checks entire dictionary against existing neuropsych conds and measures'''

   
    check_args_against_knowledge(neuro_dict)
    
    proj_lst = []    
    for k,v in neuro_dict.items():
        for i in v:
            value_len = len(i)
            for dict_val_lst in i[-1]: #get the list
                for tup in range(value_len -1):
                    concat = k + '_' + i[tup] + '_' + dict_val_lst
                    proj_lst.append(concat)

    proj = ({i: 1 for i in proj_lst})
    return proj


def get_neuro_df(uids_lst, neuro_exp_only=None,
                neuro_dict=None,
                admin=False,
                flatten_df=False):
    
    '''Can query by: 1) uids_lst + neuro_exp_only to get ALL conds/measure for experiment
                     2) uids_lst + neuro_dict to get specific conds/measures for experiments'''
    
    query = {'uID': {'$in': uids_lst}}
    proj = default_neuro_proj.copy()
    remap_cols_dict = remap_neuro_variables(neuropsych_variables)
    
    arg_compatability(uids_lst=uids_lst, neuro_exp_only=neuro_exp_only, neuro_dict=neuro_dict)
    
    if neuro_exp_only:
        if neuro_exp_only.upper() == 'VST':
            add_proj = {k:1 for k,v in remap_cols_dict.items() if 'VST' in v}
        if neuro_exp_only.upper() == 'TOLT':
            add_proj = {k:1 for k,v in remap_cols_dict.items() if 'TOLT' in v}
            
    if neuro_dict:
        need_to_format_proj = neuro_dict_proj(neuro_dict=neuro_dict)
        add_proj = {k:1 for k,v in remap_cols_dict.items() if v in need_to_format_proj.keys()}
    
    if admin:
        admin_proj = default_neuro_admin.copy()
        proj.update(admin_proj)
        docs = D.Mdb['neuropsych'].find(query, admin_proj)
        df = C.buildframe_fromdocs(docs, inds=['ID', 'np_session'])
        return df
        
    proj.update(add_proj)
    docs = D.Mdb['neuropsych'].find(query, proj)
    df = C.buildframe_fromdocs(docs, inds=['ID', 'np_session'])
    df1 = rename_neuropsych_cols(df, remap_cols_dict)
    return df1