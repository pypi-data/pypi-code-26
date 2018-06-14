import pandas as pd
import os
from main import *

def getopts(argv):
    opts = {}  # Empty dictionary to store key-value pairs.
    while argv:  # While there are arguments left to parse...
        if argv[0][0] == '-':  # Found a "-name value" pair.
            opts[argv[0]] = argv[1]  # Add key and value to the dictionary.
        argv = argv[1:]  # Reduce the argument list by copying it starting from index 1.
    return opts

def execute():
    from sys import argv
    myargs = getopts(argv)

    if '-i' in myargs:  # Example usage.
        cpout = myargs['-i']
        if cpout[-1] is not '/':
            cpout = cpout + '/'
    else: cpout = '/Users/wirtzlab/Desktop/CP_Output/'
    if '-o' in myargs:
        csvfile = myargs['-o']
    else: csvfile = '/Users/wirtzlab/Desktop/hi.csv'
    if '-m' in myargs:
        modeling =  myargs['-m'].strip()
    else: modeling = 'yes'
    if '-n' in myargs:
        clnum = myargs['-n']
    else: clnum = 15

    # cwd = os.path.abspath(os.path.dirname(__file__))
    # cwd = cwd.replace('sourcecode','')
    # direc = textfile.strip()

    if modeling[0] is 'b':
        BuildModel = True
        print 'build'
    else:
        BuildModel = False
        print 'apply'

    firstrun = True

    direc = cpout.strip()
    if direc[-1] is not '/':
        direc = direc + '/'

    main(BuildModel,firstrun,clnum,direc)

    ### below code means nothing, but needed for galaxy format ###
    d = {'dir':[direc]}
    df = pd.DataFrame(data=d)
    df.to_csv(csvfile,index=False, header=False)

    return('analysis completed')
