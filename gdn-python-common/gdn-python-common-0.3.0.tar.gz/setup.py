from os.path import dirname, join, abspath
from setuptools import setup, find_packages

ROOT_DIR = dirname(abspath(__file__))

setup(
    name='gdn-python-common',
    version='0.3.0',
    packages=find_packages(where=join(ROOT_DIR, 'src')),
    package_dir={'gramedia': 'src/gramedia'},
    url='https://engineering.gramedia.com',
    license='GPLv3+',
    author='Gramedia Digital Nusantara Team',
    install_requires=[
        'humanize>=0.5.1',
    ],
    author_email='engineering@gramedia.digital',
    description='Basic python 3.6 helper classes and functions',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
