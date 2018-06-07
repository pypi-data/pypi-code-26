#!/usr/bin/env python
""" Plot growth rate spectrum

OUTPUT:
    save figures in current directory

UPDATE:
    - 02/03/2017
      created by J.G. Chen
"""

__version__ = '2.0.0'
__date__ = '02/03/2017'

from ConfigParser import ConfigParser
import argparse
import os
import re

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import pandas as pd

#  try:
    #  from boututils.functions import sort_nicely
#  except:
    #  sort_nicely = None
    #  pass

plt.ion()
rcParams.update({'font.size': 30,
    'legend.fontsize': 26,
    'legend.labelspacing': 0.1,
    'legend.frameon': False,
    'lines.linewidth': 2,
    'lines.markersize': 14,
    'savefig.bbox': 'tight'})

parser = argparse.ArgumentParser(
    description = 'plot growth rate spectrum',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("gamma_info", nargs = '*',
    default = ['gamma_fit_info'], help = "files contain gamma info")
parser.add_argument("-x", "--xvar", nargs = '?',
    default = "ZPERIOD", help = "xaxis variable, `yvar vs. `xvar, "
                                + "`xvar should exist in `gamma_info")
parser.add_argument("-y", "--yvar", nargs = '?',
    default = "gamma", help = "yaxis variable, `yvar vs. `xvar, "
                              + "`yvar should exist in `gamma_info")
parser.add_argument("-C", "--Case", action = 'store_false',
    help = "case sensitive in `gamma_info files")
parser.add_argument("-f", "--filter", nargs = '?', default = 'gamma',
    help = "filter out `yvar using `filter, `threshold")
parser.add_argument("-t", "--threshold", nargs = '?', type = str,
    default = '< 0', help = "threshold for the filter")
parser.add_argument("-i", "--info", action = 'store_true',
    help = "print verbose information")

args = parser.parse_args()

if args.info:
    print args

if not args.Case:
    xvar = args.xvar.lower()
    yvar = args.yvar.lower()
else:
    xvar = args.xvar
    yvar = args.yvar

case_values = {}
sections = {}
filterout = {}
identities = []

# only keep files
args.gamma_info = [os.path.realpath(i)
                   for i in args.gamma_info if os.path.isfile(i)]

#  if sort_nicely:
    #  # sort string by number
    #  sort_nicely(args.gamma_info)

for info in args.gamma_info:
    idir = os.path.dirname(info)
    # identity = os.path.basename(
    #    os.path.realpath(re.sub("db|gamma_info_fit", "", idir)))
    identity = idir.split('/')
    identity = identity[-2] if identity[-1] == 'db' else identity[-1]
    while identity in case_values.keys():
        identity = identity+'1'
    try:
        for i in ['SCRATCH', 'CSCRATCH', 'HOME']:
            if i in os.environ.keys() and os.environ[i] in info:
                cases = info.replace(os.environ[i], "$"+i)
                break
    except:
        pass
    if not cases: cases = identity
    print "processing: ", cases
    identities.append(identity)

    config = ConfigParser()
    if args.Case:
        config.optionxform = str
    config.read(info)
    values = []

    filterout[identity] = []
    for section in config.sections():
        if eval("{} {}".format(config.getfloat(section, args.filter),
                               args.threshold)):
            original = False
            filterout[identity].append(section)
        else:
            original = True

        values.append(
             (config.getfloat(section, xvar),
              config.getfloat(section, yvar) if original else 0,
              section))

    values = sorted(values, key = lambda x: x[0])
    values = zip(*values)
    case_values[identity] = np.array(values[:2])
    sections[identity] = values[2]

if args.info:
    print(case_values)

secs = [i for j in sections.values() for i in j]
secs = list(set(secs))
secs.sort()

print "----------- WARNING -------------"
print "filter out '{}' if '{}' {}".format(args.yvar, args.filter,
                                          args.threshold)
for key, value in filterout.items():
    if value:
        print "{}\t :{}".format(key, value)
print "---------------------------------"

if args.info:
    print case_values

# default linestyle
colors = ['k', 'r', 'g', 'b', 'c', 'm', 'y', 'purple']
markers = ['*', 'o', 'd', 's', 'v', '>', '<', 'p']
linestyle = '-'*50
print "colors: ", colors
print "linestyle: ", linestyle
print "markers: ", markers
print "identities: ", identities
option = raw_input("colors, markers & linestyle OK?[Y/n]: ") or 'Y'
if option not in ['Y', 'y', 'YES', 'yes', 'Yes']:
    linestyle = raw_input("input linestyle: ")
    linestyle = re.split(";|,", re.sub("\"|'| ", "", linestyle))
    colors = [ ls[0] for ls in linestyle]
    if args.info:
        print "linestyle: ", linestyle
        print "colors: ", colors

colors = colors
markers = markers
linestyle = linestyle

plt.figure(figsize=[12,8], facecolor='w')
for key, ls , i in zip(identities, linestyle, range(len(colors))):
    usize = len(np.unique(case_values[key][0, :]))
    osize = case_values[key].shape[1]
    if (usize > 1) or (osize == 1):
        plt.plot(case_values[key][0, :], case_values[key][1, :],
                 marker=markers[i],
                 ls=linestyle[i],
                 color=colors[i],
                 label=key)
    else:
        xvar = ''
        xvalue = [secs.index(i) for i in sections[key]]
        yvalue = case_values[key][1, :]
        yvalue = [y for x, y in sorted(zip(xvalue, yvalue))]
        xvalue.sort()
        plt.plot(xvalue, yvalue,
                 marker=markers[i], ls=linestyle[i], color=colors[i],
                 label=key)
if xvar == '':
    plt.xticks(range(len(secs)), secs, rotation=45, ha='right')

l = plt.legend(loc=0)

if xvar.lower() in ["zperiod", 'n']:
    plt.xlabel('toroidal mode number')
else:
    plt.xlabel(xvar)

if yvar.lower() == "gamma":
    plt.ylabel('$\gamma/\omega_A$')
else:
    plt.ylabel(yvar)
plt.grid('on')
plt.tight_layout()

option = raw_input("Change Fig?[Y/n]: ") or 'Y'
if option in ['Y', 'y', 'YES', 'yes', 'Yes']:
    print "input python commands, type 'q' to exit: "
    while True:
        command = raw_input("   ")
        try:
            exec(command)
        except:
            if command in ["EOF", "eof", "exit", "quit", "q"]:
                break
            print "Error command, try again:"
            pass

for icolor, text in zip(colors, l.get_texts()):
    text.set_color(icolor)

title = raw_input('figure title: ')
plt.title(title)
figname = raw_input('figure name: ')
if figname:
    print "saving figs ..."
    plt.savefig(figname + '.png')
    plt.savefig(figname + '.eps')
