import os



def batch_change_runletter(path, bad_letter, good_letter):
	'''used to change run letter ONLY '''

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
    '''originally used to change original.cnt to orig.cnt '''

    for r,d,f in os.walk(path):
        for n in f:
            if bad_name_str in n:
                new_fname = n.replace(bad_name_str, new_name_str)
                os.rename(os.path.join(r,n), os.path.join(r, new_fname))
                print('changed')