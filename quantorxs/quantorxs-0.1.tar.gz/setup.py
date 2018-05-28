from setuptools import setup
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file

long_description = """
QUANTORXS : QUANTification of ORganics by X-ray Spectrosocopy
=============================================================

QUANTORXS is an opensource program to automatically analyze X-ray
spectroscopy spectra of Carbon, Nitrogen and Oxygen K-edges edges to
quantify the concentration of functional groups and the elemental ratios
N/C and O/C using a novel quantification method that will soon be
pusblished in a peer-reviewed scientific article.

QUANTORXS performs the following tasks automatically:

-  Load the data from the file(s)
-  Remove background
-  Normalize the spectra
-  Generate a model of the fine structure a fit it to the experimental
   data
-  Calculate the functional groups abundances and elemental rations from
   the results of the fit
-  Generate an Excel file and multiple figures with the results and
   normalised spectra files.

For the full documentation go to `QuantORXS' GitHub
repository <https://github.com/CorentinLG/QuantORXS>`__.
"""


setup(
    name='quantorxs',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.1',

    description='XANES quantification of functional group abundances',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/corentinlg/quantorxs',

    # Author details
    author='Corentin Le Guillou',
    author_email='corentin.le-guillou@univ-lille1.fr',

    # Choose your license
    license='GPLv3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
    ],

    keywords='XANES abundance quantification',
    packages=[
        "quantorxs",
        "quantorxs.tests"],

    install_requires=[
        'numpy',
        'scipy',
        'xlsxwriter',
        'matplotlib'],

    package_data={
        'quantorxs': ['data/*.f1f2',
                      'data/example_spectra/*.txt',
                      'data/images/quantorxs_logo.gif', ]
    },

    entry_points={
        'gui_scripts': ['quantorxs_gui = quantorxs.gui_tk:main'],
        'console_scripts': ['quantorxs = quantorxs.cli:main']
    },
)
