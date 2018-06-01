'''
Washi

Usage:
    washi init 

Options:
    -h --help Show this screen
'''

from docopt import docopt, DocoptExit
import os
import cmd
import sys

def init_washi():
    """Usage: washi init"""
    #Create folders
    folders = ['analysis', 'setup', 'data']
    for folder in folders:
        os.mkdir(folder)
    #Create experiment info file
    open('EXPINFO.md', 'w')


def main():
    args = docopt(__doc__,
                  options_first=True)
    if args['init']:
        init_washi()

    
