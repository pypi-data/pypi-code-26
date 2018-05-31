from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

version = '1.0'

install_requires = [
    'Pillow==5.1.0',
    'strakspycoin',
    'qrcode==6.0',
    'six==1.11.0',
    'urllib3==1.22'
]


setup(name='strakspos',
    version=version,
    description="STRAKS POS",
    long_description=README,
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.6',
        
    ],
    keywords='STRAKS STAK POS minipos',
    author='Freeman',
    author_email='freeman@straks.tech',
    url='https://straks.tech',
    license='Apache',
    packages=['src'],
    #package_dir = {'src': 'minipos'},include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['strakspos=src.minipos']
    },
    include_package_data=True
)
