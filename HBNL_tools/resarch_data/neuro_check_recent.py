#!/usr/bin/env python
import os
import re
import sys
from collections import Counter
from collections import defaultdict
import datetime

def restart_script():
    input('Please fix then press enter to restart program')
    neuro(fp)
    
def neuro(fp):
    
    #1 -- check for unknown file types
    for r,d,f in os.walk(fp):
        for n in f:
            if not n.endswith(("xml", "txt", "_sum.txt")):
                path  = os.path.join(r,n)
                print('\n', 'Error: Unknown file types found --', path)
                #restart_script()


    #2 -- check that all IDS have 8 numbers and all sum/txt files having CBST/TOLT in filename
    for r,d, f in os.walk(fp):
        for n in f:
            if n.endswith(("_sum.txt", 'txt')):
                split = n.split("_")
                if len(split[0]) != 8:
                    print('Error: ID Incorrect Length -- ', split)
                    restart_script()
                else:
                    if split[1] == 'CBST':
                        pass
                    elif split[1] == 'TOLT':
                        pass
                    else:
                        print('Error: Wrong experiment name -- ', split[0])
                        #restart_script() 

    #3 -- create dictionary of each element in the filename 
    sum_txt_dict = {}
    txt_dict = {}
    xml_fname_dict = {}

    for r,d,f in os.walk(fp):
        ids_sumtxt = []
        version_sumtxt = []
        run_sumtxt = []
        ext_sumtxt = []

        ids_txt=[]
        version_txt = []
        run_txt = []
        ext_txt = []

        ext_xml = []

        ids_xml = []
        run_xml = []
        ext_xml = []
        for n in f:
            if n.endswith('txt'):
                if n.endswith('_sum.txt'):
                    sumtxt_split = n.split('_')
                    ids_sumtxt.append(sumtxt_split[0])
                    version_sumtxt.append(sumtxt_split[2])
                    run_sumtxt.append(sumtxt_split[3])
                    ext_sumtxt.append(sumtxt_split[-1])
                else:
                    txt_split = re.split(r'[_.]', n)
                    ids_txt.append(txt_split[0])
                    version_txt.append(txt_split[2])
                    run_txt.append(txt_split[3])
                    ext_txt.append(txt_split[-1])
            if n.endswith('xml'):
                xml_split = n.split('_')
                ids_xml.append(xml_split[0])
                run_xml.append(xml_split[1])
                ext_xml.append(xml_split[2])

        tup_sumtxt = version_sumtxt, run_sumtxt, ext_sumtxt
        tup_txt = version_txt, run_txt, ext_txt
        tup_xml = run_xml, ext_xml

        for i in ids_sumtxt:
            sum_txt_dict[i] = tup_sumtxt

        for j in ids_txt:
            txt_dict[j] = tup_txt

        for k in ids_xml:
            xml_fname_dict[i] = tup_xml 

        ids_total = ids_sumtxt + ids_txt + ids_xml
        ids_count_dict = Counter(ids_total)
        for k,v in ids_count_dict.items():
            if v != 5:
                print('Error: There\'s an ID missing from', k)
                #restart_script()

    #####might need to add check to make sure sum_txt & txt dict keys are same length???

    #4 -- check for version, run leter, and # of extensions for sum_txt files 
    for k,v in sum_txt_dict.items():
        if len(list(set(v[0]))) != 1:
            print('Error: Check version number for sum_txt file', k)
        for i in v[0]:
            if i != '1':
                print('Error: Check version number for sum_txt file', k)
        if len(list(set(v[1]))) != 1:
            print('Error: Check run letter for sum_txt file', k)
            restart_script()
        if len(v[2]) != 2:
            print('Error: Missing sum_txt file for ID', k)


    #5 -- check for version, run leter, and # of extensions for txt files 
    for k,v in txt_dict.items():
        if len(list(set(v[0]))) != 1:
            print('Error: Check version number for txt file', k)
        for i in v[0]:
            if i != '1':
                print('Error: Check version number for txt file', k)
        if len(list(set(v[1]))) != 1:
            print('Error: Check run letter for txt file', k)
            restart_script()
        if len(v[2]) != 2:
            print('Error: Missing txt file for ID txt file', k)


    #6 -- check to see if version and run letter are identical across txt & sum_txt files
    for k,v in sum_txt_dict.items():
        if k in txt_dict.keys():
            if not v[0] == txt_dict[k][0]:
                print('Error: Version number between sum.txt & txt files don\'t match for', k)
            if not v[1]  == txt_dict[k][1]:
                print('Error: Run letter between sum.txt & txt files don\'t match for', k)
                restart_script()

    #7 -- check for things inside xml file            
    xml = [os.path.join(root,name) for root,dirs,files in os.walk(fp) for name in files if name.endswith(".xml")]

    within_xml_id = []
    within_xml_run = []
    xml_motiv = []


    xml_dict_new = {}
    for i in xml:
        lst_xml_id = []
        dob_lst = []
        testdate_lst = []
        gender_lst = []
        hand_lst = []
        with open(i) as f:
            for line in f:

                if line.startswith('  <Sub'):
                    lst_xml_id.extend(re.findall(r'<SubjectID>(.*?)</SubjectID>', line))
                    within_xml_id.extend(re.findall(r'<SubjectID>(.*?)</SubjectID>', line))
                if line.startswith('  <Sess'):
                    within_xml_run.extend(re.findall(r'<SessionCode>(.*?)</SessionCode>', line))
                if line.startswith('  <Motivation>'):
                    xml_motiv.extend(re.findall(r'<Motivation>(.*?)</Motivation>', line))
                if line.startswith('  <DOB>'):
                    dob_lst.extend(re.findall(r'<DOB>(.*?)</DOB>', line))
                if line.startswith('  <TestDate>'):
                    testdate_lst.extend(re.findall(r'<TestDate>(.*?)</TestDate>', line))
                if line.startswith('  <Gender>'):
                    gender_lst.extend(re.findall(r'<Gender>(.*?)</Gender>', line))
                if line.startswith('  <Hand>'):
                    hand_lst.extend(re.findall(r'<Hand>(.*?)</Hand>', line))

                xml_tuples = dob_lst, testdate_lst, gender_lst, hand_lst
                for i in lst_xml_id:
                    xml_dict_new[i] = xml_tuples

    now = datetime.datetime.now().year

    #8 -- xml check for accurate DOB, testdate, & that gender and version start with uppercase letter
    for k,v in xml_dict_new.items():
        for i in v[0]:
            date_split = i.split('/')
            year = int(date_split[-1])
            if year > 2015:
                print('Error: Check DOB in xml file for', k)
        for j in v[1]:
            testdate_split = j.split('/')
            year_test = int(testdate_split[-1])
            if year_test != now:
                print('Error: Check test date in xml file for', k)
        for l in v[2]:
            if not l[0].isupper(): #maybe str.istitle() would be better?
                print('Error: Make gender uppercase in xml file for', k)
        for m in v[3]:
            if not m[0].isupper():
                print('Error: Make handedness uppercase in xml file for', k)

    inside_xml = dict(zip(within_xml_id, within_xml_run))

    #9 -- xml check for length of sub IDs 
    xml_ids = [('Error: Check inside xml file for sub ID', i) for i in within_xml_id if len(i) != 8]
    if len(xml_ids) != 0:
        print(xml_ids)

    #10 -- 11 will only work if 2 xml dicts have the same keys 
    missing_xml_keys = set(xml_fname_dict.keys() ^ inside_xml.keys())
    if len(list(missing_xml_keys)) > 0:
        print('Error: Check', k, 'folder for missing xml files' )
        restart_script()

    #11 -- check to see if run letter within xml matches xml filename    
    for k,v in xml_fname_dict.items():
        for l in v[0]:
            if k in inside_xml.keys():
                if l not in inside_xml[k]:
                    print('Error: Check', k, 'folder for mismatch between xml run letter and xml filename run letter')
                    restart_script()

    #12 -- since we know txt & sum_txt run letters are identical & that inside and xml fname run letters are identical...
    #12... check run letters against xml & sum_txt files 
    for k,v in txt_dict.items():
        run_letter = v[1][0][0]
        if k in inside_xml.keys():
            if run_letter not in inside_xml.values():
                print('Error: Check', k, 'folder for mismatch between xml run letter and xml filename run letter')
                restart_script()
            
            
    input('Finished.  Press enter to close script')

fp = input('Enter your neuropsych folders path   ' )

neuro(fp)