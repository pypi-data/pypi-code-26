#!/usr/bin/env python3

import json
import os
import sys
import yaml
import getopt


#URL='http://localhost:2379'
URL='https://etcd.wongsrus.net.au'

keys_cnt = 0
keys = []
top_str = ''
app_str = ''
env_str = ''
node_str = ''
DEBUG=0
DRYRUN=0
SEE_JSON=0

#loaded_nodes_dict = yaml.load(open('servers.yaml'))

def debug (msg):
    if DEBUG:
      print (msg + "\n" )

def doOs (cmd_args):
    if len(cmd_args) < 1:
      return
    thecmd = ' '.join(cmd_args[1:])
    f = os.popen(thecmd)
#    print '%s\n' % (f.read())
    print ('{}\n'.format(f.read()))

def process_help ():
    print ("xx : exit ")
    print ("/  : search")

def process_search ():
		pat = input("\npattern: ")



def  _getopts():
  global DRYRUN, DEBUG, SEE_JSON
  try:
    opts, args = getopt.getopt(sys.argv[1:],"hdj",["headless", "dryrun"])
  except getopt.GetoptError:
    usage('Error:')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      usage()
      exit(0)
    if opt == '-j':
      SEE_JSON=1
    if opt == '-d':
      DEBUG=1
    if opt == '--dryrun':
      DRYRUN = True




def main ():
  _getopts()



if __name__ == '__main__':
  main()

