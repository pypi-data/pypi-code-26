import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "washi",
    version = "0.0.1",
    author = "Kobi Felton",
    author_email = "kobi.c.f@gmail.com",
    description = ("Scripts to easily organize research"),
    packages = find_packages(),
    include_package_data=True,
    install_requires = ['docopt'],
    long_description_content_type = 'text/markdown',
    long_description = read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
    entry_points = {
        'console_scripts': [
            'washi=washi.washi:main'
        ],
    }
)