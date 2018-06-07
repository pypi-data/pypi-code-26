#!python
"""This script is for parameters scanning of BOUT++.

EXAMPLE
-------

    $ scan.py -v ZPERIOD -r '1, 2, 4, 5' -t template -p mode_n
    it will create a serial dirs according to 'template':
        >> mode_n1, mode_n2, mode_n4, mode_n5
"""
__version__ = '1.0.0'
__date__ = '02/08/2017'

import argparse
import subprocess
import os
import sys

parser = argparse.ArgumentParser(
    description='Parameters Scanning For BOUT++',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    '-d', '--data', action='store_true',
    help='the path is data_path')
parser.add_argument(
    '-i', '--info', action='store_true',
    help='Print more informations')
parser.add_argument(
    '-p', '--prefix', nargs='?', default='n',
    help='prefix of dirname')
parser.add_argument(
    '-r', '--range', nargs='?',
    default='5, 10 ,20, 30, 40, 50',
    help='range of variable for scanning, string delimited with comma')
parser.add_argument(
    '-t', '--template', nargs='?', default='dia-n2',
    help='template for parameters scanning, only change \
        the value of option "var" in BOUT.inp')
parser.add_argument(
    '-v', '--var', nargs='?', default='ZPERIOD',
    help='name of variable for scanning')

args = parser.parse_args()
if args.info:
    print args

template = args.template
vrange = args.range
var = args.var
if args.data:
    data = ''
else:
    data = 'data'

if not (os.path.exists(template) and
        os.path.exists(os.path.join(template, data, 'BOUT.inp'))):
    sys.exit("no such template: {} or BOUT.inp\nDo Nothing!!!".format(
        template))
else:
    # exclude case: 'rsync -auHv a b' --> 'rsync -auHv a/ b'
    template = os.path.relpath(template)

if '.' in vrange:  # range data: float
    vrange = [float(i) for i in vrange.split(',')]
else:
    vrange = [int(i) for i in vrange.split(',')]

print "scanning info:"
print "tamplate:\t", template
print "scan var:\t", var
print "range: \t\t", vrange
print "prefix:\t", args.prefix

yn = raw_input("ok? ([Y]/n): ") or 'y'
if yn not in ['y', 'Y', 'yes', 'YES', 'yes']:
    sys.exit("Do nothing!!!")

# match line starts with var
old_opt = "^{}\s*=\s*[0-9\.]*".format(var)

exists_dir = []
scan_dir = []
for i in vrange:
    subdir = args.prefix + str(i)
    new_opt = var + " = " + str(i)

    if not os.path.exists(subdir):
        # os.system('copydir.sh '+ template + ' '+ subdir)
        output = subprocess.check_output(
            'rsync -avHh --exclude=BOUT*nc --exclude=*out \
            --exclude=BOUT.log* {}/ {}'.format(template, subdir),
            shell=True)
        print output
        scan_dir.append(subdir)
    else:
        print "\nWARNING: {} already exists!!!!".format(subdir)
        print "           Continuing ...\n"
        exists_dir.append(subdir)
        continue

    subprocess.check_call('sed -i "s/{}/{}/" {}/BOUT.inp'.format(
        old_opt, new_opt, os.path.join(subdir, data)), shell=True)

    # compare the files
    print "\n ###### diff {} {}\n".format(template, subdir)
    try:
        subprocess.check_output(
            "diff {}/BOUT.inp {}/BOUT.inp".format(
                os.path.join(template, data),
                os.path.join(subdir, data)),
            shell=True)
    except subprocess.CalledProcessError as cpe:
        # diff return 1(there are differences) or >1(ERROR)
        if cpe.returncode > 1:
            print "ERROR: ", cpe.output
            raise subprocess.CalledProcessError
        else:
            print cpe.output
    print "--" * 20

if exists_dir:
    print "The following dirs already exist:"
    print exists_dir
if scan_dir:
    print "Successfully create dirs:"
    print scan_dir
