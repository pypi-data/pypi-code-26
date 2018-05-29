#!/usr/bin/env python
# vim: set fileencoding=utf-8 nofoldenable:

from setuptools import setup


VERSION = "1.0"

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
