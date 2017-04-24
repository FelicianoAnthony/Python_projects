from db import organization as O
from db import compilation as C
import pandas as pd

def create_mt(experiment, measure, flat_df=False, **optargs):
    ''' Using experiment name and measure of interest ('amp' or 'lat') as 'normal args' -- Using either 
    uID or ID/session lists as keyworded args -- returns data frame of mt files which can be filtered 
    by condition/peak and channels.
    normal args = str(experiment), list(measure)
    flat_df = False -- specify True if non-hierarchical data frame desired 
    keyworded args = list(ID), list(session), tuple(uID), list(cond_peaks), list(chans)
    **cond_peaks and chans must be used together**'''
        
    #search by uID or separate ID/session lists 
    if ('ID' in optargs and 'session' in optargs):
        uIDs = ['_'.join((IDs, sessions)) for IDs, sessions in zip(optargs['ID'], optargs['session'])]
    elif ('uID' in optargs):
        uIDs = optargs['uID']
    else:
        print('Missing sample search parameters')

    #create query    
    query = {'uID': {'$in': uIDs}}

    #format projection to return specific cond/peak/chan combos...
    #...or use default projection of *all* conds/peaks/chans
    if ('cond_peaks' in optargs and 'chans' in optargs):   
        proj = C.format_ERPprojection(experiment, optargs['cond_peaks'], optargs['chans'], measure)  
        proj.update({'experiment': experiment}) #probably need to change this 
        docs = O.Mdb['ERPpeaks'].find(query, proj)
    else:
        default_proj = {"ID":1, "session":1, "_id":0, experiment:1, "experiment":1}
        docs = O.Mdb['ERPpeaks'].find(query, default_proj)
        
    #build data frame from Mongodocs
    df = C.buildframe_fromdocs(docs, inds=['ID', 'session', 'experiment'])
    
    #if query uses format_ERPproj... exp_name filepath col needs to be removed...
    #...filepath found within exp 
    filepath_col = experiment + '_' + 'filepath'
    if filepath_col in df.columns: 
        del df[filepath_col]
    else:
        pass
    
    #return non-hierarchical data frame if boolean is True
    if flat_df == True:
        return df
    
    #format column names and create multi-index
    df.columns = [col[4:] for col in df.columns if col.startswith(experiment)]
    df.columns = pd.MultiIndex.from_tuples([tuple(col_name.split('_')) for col_name in df.columns])
    
    #prettify
    df_stacked = df.stack(level=[0,2]).reset_index()
    df_renamed = df_stacked.rename(columns={'level_3':'condition', 'level_4':'channel'})
    df_multi = df_renamed.set_index(keys=['ID', 'experiment', 'session', 'condition', 'channel'])
    return df_multi