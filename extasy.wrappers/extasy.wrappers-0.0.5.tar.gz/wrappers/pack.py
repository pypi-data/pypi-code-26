import os
import tempfile

def pack(file_list, defdir=None):
    outfile = tempfile.NamedTemporaryFile(suffix='.alb', dir=defdir, delete=False)
    for fname in file_list:
        outfile.write(fname + '\n')
        
    return outfile.name

def unpack(trajfile, defdir=None):

    cfiles = []
    with open(trajfile) as f:
        cfiles = [line[:-1] for line in f]

    return cfiles

