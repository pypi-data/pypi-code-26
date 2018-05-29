#!/usr/bin/env python
# vim: set fileencoding=utf-8 nofoldenable:

from setuptools import setup


VERSION = "1.2"

classifiers = [
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Natural Language :: English',
    'Operating System :: Unix',
    'Programming Language :: Python',
    'Topic :: Internet',
    ]

LONG_DESC = """Counts network traffic to and from local addresses using pcap.
Stores data in an SQLite database for 60 seconds periods.  Generates simple
reports.  Reports can have IP address labelled.  Other reports can be generated
using SQL and custom scripts.  Labels traffic during 1:00 AM and 7:00 AM as
free (that's how my ISP works).

This package install only one script named `traflog`.

Start collecting data::

    $ sudo traflog --net 192.168.1.0 --mask 255.255.255.0 /var/lib/traffic.sqlite

(You probably want to run this as a service.)

Generate report::

    $ traflog --report --hours=24 /var/lib/traffic.sqlite
    addr              nonfree      free
    -----------------------------------
    192.168.1.5          0.00      0.00  router.tplink
    192.168.1.103      318.00      1.00  julia.samsung
    192.168.1.104       81.00      0.00  rebekka
    192.168.1.105        0.00      0.00  ?
    192.168.1.108       17.00      0.00  ?
    192.168.1.125      259.00     15.00  umonkey.dell
"""


setup(
    name = 'traflog',
    version = VERSION,
    author = 'Justin Forest',
    author_email = 'hex@umonkey.net',
    url = 'http://bitbucket.org/umonkey/traflog_py',

    packages = ['traflog'],
    scripts = ['bin/traflog'],

    install_requires = ['sqlite3', 'pcap'],

    classifiers = classifiers,
    description = 'Simple traffic accounter, based on pcap.',
    long_description = LONG_DESC,
    license = 'GNU GPL',
)
