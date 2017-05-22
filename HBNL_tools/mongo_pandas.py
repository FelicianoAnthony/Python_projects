from db import database as D
import db.compilation as C
import pandas as pd
from collections import defaultdict

erp_condpeaks = {'aod': ['nt_N1', 'nt_P2', 't_N1', 't_P3'],
                 'vp3': ['nt_N1', 'nt_P3', 't_N1', 't_P3', 'nv_N1', 'nv_P3'],
                 'ant': ['a_N4', 'a_P3', 'j_N4', 'j_P3', 'w_N4', 'w_P3']}

electrodes_62 = ['FP1', 'FP2', 'F7' , 'F8' , 'AF1', 'AF2', 'FZ' ,
 'F4' , 'F3' , 'FC6', 'FC5', 'FC2', 'FC1', 'T8' , 'T7' , 'CZ' ,
  'C3' , 'C4' , 'CP5', 'CP6', 'CP1', 'CP2', 'P3' , 'P4' , 'PZ' ,
   'P8' , 'P7' , 'PO2', 'PO1', 'O2' , 'O1' , 'AF7', 'AF8',
    'F5' , 'F6' , 'FT7', 'FT8', 'FPZ', 'FC4', 'FC3', 'C6' , 'C5' ,
     'F2' , 'F1' , 'TP8', 'TP7', 'AFZ', 'CP3', 'CP4', 'P5' ,
      'P6' , 'C1' , 'C2' , 'PO7', 'PO8', 'FCZ', 'POZ', 'OZ' ,
       'P2' , 'P1' , 'CPZ'] #removed X


erp_exp_condpeakchans = dict()
erp_exp_condpeakchans['aod'] = [('nt', 'N1', ['FZ', 'PZ']),
                                ('nt', 'P2', ['CZ', 'F4', 'F3']),
                                ('t', 'N1', ['FZ', 'PZ']),
                                ('t', 'P3', ['PZ']), ]
erp_exp_condpeakchans['vp3'] = [('nt', 'N1', ['FZ', 'PZ']),
                                ('nt', 'P3', ['PZ', 'F4', 'F3']),
                                ('nv', 'N1', ['P4', 'PZ', 'P3']),
                                ('nv', 'P3', ['PZ']),
                                ('t', 'N1', ['P4', 'PZ', 'P3']),
                                ('t', 'P3', ['CZ', 'PZ']), ]


default_measures = ['amp', 'lat']
default_ERPproj = {"ID":1, "session":1, "_id":0}



def parse_mtargs(experiment, cond_peaks=None, channels=None, measure=None):
    ''' parses default arguments for create_matdf function and returns the projection '''
   
    if not cond_peaks:
        cond_peaks = erp_condpeaks[experiment]
   
    if not channels:
        channels = electrodes_62.copy()
   
    if not measure:
        measure = default_measures.copy()
       
    proj = format_ERPprojection(experiment, cond_peaks, channels, measures)
   
    return proj

def parse_mtargs_exp_only(experiment, cond_peaks=None, channels=None, measure=None):
    ''' parses default arguments for create_matdf function and returns the projection '''
   
    if not cond_peaks:
        cond_peaks = erp_condpeaks[experiment]
   
    if not channels:
        channels = electrodes_62.copy()
   
    if not measure:
        measure = default_measures.copy()
       
    proj = C.format_ERPprojection(experiment, cond_peaks, channels, measures)
   
    return proj

#works with exp_cond_peaks argument in create_matdf
def format_ERPprojection(experiment, conds_peaks, chans, measures=['amp', 'lat']):
    ''' format a projection to retrieve specific ERP peak information 
        Example args: experiment = []
                      cond_peaks = []
                      chans = []
                      measures = []'''
    
    proj = default_ERPproj.copy()
    proj.update({'.'.join([exp, cp, chan, m]): 1
                 for exp in experiment for cp in conds_peaks for chan in chans for m in measures})
    return proj



#advanced querying with crazy dictionary 
def parse_mtdict_args(erp_exp_condpeakschans, measures = None):
    ''' parses exp_condpeaks_chans arg in create_matdf
        Example args: erp_exp_condpeakschans = ['aod'] = [('nt', 'N1', ['FZ', 'PZ']),
                                                          ('nt', 'P2', ['CZ', 'F4', 'F3'])]  
                     measures = ['amp']'''
    
    if not measures:
        
        m = ['amp', 'lat']
        proj = format_ERPprojection_dict(erp_exp_condpeakschans, m)

    if measures:
        
        proj = format_ERPprojection_dict(erp_exp_condpeakschans, measures)
        
    return proj


def format_ERPprojection_dict(erp_exp_condpeakschans, measures=['amp', 'lat']):
    '''format a projection with input being erp_exp_condpeakschans dictionary '''

    proj = default_ERPproj.copy()
    for k,v in erp_exp_condpeakchans.items():
        cpc_lst = v
        for cond_peak_chans in cpc_lst:
            conds, peaks, chans = cond_peak_chans
            for chan in chans:
                for m in measures:
                    key = k + '.' + conds + '_' + peaks + '.' + chan + '.' + m
                    proj[key] = 1
    return proj 



def create_matdf(uIDs, experiment = None, exp_cond_peaks=None, channels=None, 
                 measure=None, exp_condpeaks_chans=None, flatten_df = False):
    '''
    Returns multi-indexed data frame that returns any combination of condition_peak, channels, and measures.
    flatten_df = True for non-hierarchical data frame'''
    
    if experiment:
        query = {'uID': {'$in': uIDs}} #how to check for multiple eperiments 
        
        proj = default_ERPproj.copy()
        
        add_proj = parse_mtargs_exp_only(experiment, cond_peaks=None, channels=channels, measure=measure)
        
        proj.update(add_proj)

        docs = D.Mdb['ERPpeaks'].find(query, proj)
        df = C.buildframe_fromdocs(docs, inds=['ID', 'session', 'experiment'])
        return df
        
    if exp_condpeaks_chans:
        
        query = {'uID': {'$in': uIDs}} #how to check for multiple eperiments 
        proj = default_ERPproj.copy()

        add_proj = parse_mtdict_args(erp_exp_condpeakchans, measures = measure)

        proj.update(add_proj)

        docs = D.Mdb['ERPpeaks'].find(query, proj)

    if not exp_condpeaks_chans:
        
        exps = []
        c_peak = []
        for k,v in exp_cond_peaks.items():
            exps.append(k)
            c_peak.extend(v)
        
        query = {'uID': {'$in': uIDs}} ##exps: {'$exists': True}
        proj = default_ERPproj.copy()

        add_proj = parse_mtargs(exps, c_peak, channels, measure)

        proj.update(add_proj)

        docs = D.Mdb['ERPpeaks'].find(query, proj)
        
        
   
    df = C.buildframe_fromdocs(docs, inds=['ID', 'session', 'experiment'])
    

   
    if flatten_df:
        return df
    else:
        df.columns = pd.MultiIndex.from_tuples([tuple(col_name.split('_')) for col_name in df.columns])
        df_stacked = df.stack(level=[0,3]).reset_index()
        df_renamed = df_stacked.rename(columns={'level_2':'experiment', 'level_3':'condition'})
        df_multi = df_renamed.set_index(keys=['ID', 'experiment', 'session', 'condition'])
        return df_multi