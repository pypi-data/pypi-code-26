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

process = ''

class Process:

  data = 0

  def __init__(self, data=0):
    self.data = data

  def debug (self, msg):
      if DEBUG:
        print (msg + "\n" )

  def doOs (self, cmd_args):
      if len(cmd_args) < 1:
        return
      thecmd = ' '.join(cmd_args[1:])
      f = os.popen(thecmd)
  #    print '%s\n' % (f.read())
      print ('{}\n'.format(f.read()))

  def process_search (self):
      pat = input("\npattern: ")

  def process_help (self):
      with open(os.path.dirname(__file__) + '/README.txt', 'r') as fin:
  #    with open('README.txt', 'r') as fin:
        data = fin.read()

      data += "\ninteractive commands"
      data += "\n--------------------"
      data += "\n   xx : exit "
      data += "\n   /  : search   -- experimental"
      print (data)
  #      data=fin.read().replace('\n', '')
      return (data)


def  _getopts():
  global DRYRUN, DEBUG, SEE_JSON
  try:
    opts, args = getopt.getopt(sys.argv[1:],"hdj",["headless", "dryrun"])
  except getopt.GetoptError:
    usage('Error:')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      process.process_help()
      exit(0)
    if opt == '-j':
      SEE_JSON=1
    if opt == '-d':
      DEBUG=1
    if opt == '--dryrun':
      DRYRUN = True



def main ():
  global process

  process = Process()

  _getopts()




if __name__ == '__main__':
  main()

