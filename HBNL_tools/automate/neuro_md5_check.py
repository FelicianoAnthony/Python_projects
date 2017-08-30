#!/usr/bin/env python
import hashlib
from collections import defaultdict
import os 

def md5(path):
    '''generate md5 - -read file in binary mode'''
    with open(path, "rb") as f:
        data = f.read()
        md5_return = hashlib.md5(data).hexdigest()
        return md5_return
    
    
    
def md5_check_walk(dir_path):
    '''given a dir path -- comapres md5 checksums across files and identifies duplicate files '''
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
   
    input('Press enter to close script')

path = input('enter your path   ')

md5_check_walk(path)