#!/usr/bin/env python
from glob import glob
import os

def change_neuro_run_letter(fp, bad_letter, good_letter):
    '''given a path to a neuropsych folder with 1 session in it,
       changes run letter in file name and within xml file'''

    #
    for full_path in glob(fp +'/*.txt'):
        fname = os.path.basename(full_path)
        if fname[15:17] == bad_letter:
            repl = fname.replace(bad_letter, good_letter)
            new_path = os.path.join(os.path.dirname(full_path), repl)
            #print(new_path)
            os.rename(full_path, new_path)
            print('New Filename: ', repl)

    for full_path_xml in glob(fp +'/*.xml'):
        fname_xml = os.path.basename(full_path_xml)
        if fname_xml.split('_')[1] == bad_letter[-1:]:
            repl_xml = fname_xml.replace(bad_letter[-1:], good_letter[-1:])
            new_path_xml = os.path.join(os.path.dirname(full_path_xml), repl_xml)
            os.rename(full_path_xml, new_path_xml)
            print('New FIlename: ', repl_xml)

    xml_file = [os.path.join(r,n) for r,d,f in os.walk(fp) for n in f if n.endswith('xml')]

    bad_letter_xml = '>' + bad_letter[-1:] + '<'
    good_letter_xml = '>' + good_letter[-1:] + '<'
    
    s  = open(xml_file[0], 'r+').read()
    s = s.replace(bad_letter_xml, good_letter_xml) 
    f=open(xml_file[0], 'w')
    f.write(s)
    f.close()
    
    input("Press enter to close script.")
    
filepath_input = input("Enter filepath -- no quotes  ")
bad_letter_input = input("Enter incorrect run letter -- '_d  '")
good_letter_input = input("Enter correct run letter -- '_c  '")


change_neuro_run_letter(filepath_input, bad_letter_input, good_letter_input)