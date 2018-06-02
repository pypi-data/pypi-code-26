##########################################
##### Setup File
##########################################

from setuptools import setup, find_packages

setup(
  name = 'genetiks',
  packages = find_packages(),

  description = 'An easy to configure and multi-threaded library for Genetic Algorithms.',
  version = '0.1.1',

  author = 'enescnkr',
  author_email = 'enescankiri@gmail.com',

  url = 'https://github.com/vonReany/GeneticAlgorithms',
  download_url = 'https://github.com/vonReany/GeneticAlgorithms/archive/0.1.1.tar.gz',

  keywords = ['genetic algorithm', 'genetics', 'evolutionary algorithms', 'genetic optimization', 'python genetic', 'optimization', 'multi threaded', 'multi processing'],

  classifiers = [
    "Development Status :: 2 - Pre-Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3.5",
    "Topic :: Scientific/Engineering",
    "Topic :: Software Development",
    ],
)