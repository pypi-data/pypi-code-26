"""setup.py file."""

from setuptools import setup, find_packages

__author__ = 'David Barroso <dbarrosop@dravetech.com>'

with open("requirements.txt", "r") as fs:
    reqs = [r for r in fs.read().splitlines() if (len(r) > 0 and not r.startswith("#"))]

setup(
    name="napalm-asa",
    version="0.1.1",
    packages=find_packages(),
    author="Diogo Assumpcao",
    author_email="diogo.assumpcao@gmail.com",
    description="Network Automation and Programmability Abstraction Layer with Multivendor support",
    classifiers=[
        'Topic :: Utilities',
         'Programming Language :: Python',
         'Programming Language :: Python :: 2',
         'Programming Language :: Python :: 2.7',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
    ],
    url="https://github.com/napalm-automation-community/napalm-asa",
    include_package_data=True,
    install_requires=reqs,
)
