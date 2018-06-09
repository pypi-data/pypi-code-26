from setuptools import setup, find_packages
# from distutils.core import setup, find_packages
from os.path import abspath, dirname, join
from pr_clt import __version__

this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.rst'), encoding='utf-8') as file:
    long_description = file.read()

setup(
	name='pr_clt',
	python_requires='>=3.6.2',
	version=__version__,
    description='Command Line Tool that searches for Pull Requests in Bitbucket account',
	long_description=long_description,
    author='Erik Duisheev',
    author_email='duisheev_e@auca.kg',
	license='UNLICENSE',
	url='https://bitbucket.org/erik31/pullrequest-clt/',  
	packages=find_packages(),
	entry_points = {
        'console_scripts': [
            'pr_clt=pr_clt.pr_clt:main'
        ]
    }
)