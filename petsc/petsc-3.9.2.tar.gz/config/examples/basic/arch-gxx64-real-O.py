#!/usr/bin/python
if __name__ == '__main__':
  import sys
  import os
  sys.path.insert(0, os.path.abspath('config'))
  import configure
  configure_options = [
    '--with-cc=gcc',
    '--with-cxx=g++',
    '--with-clanguage=C++',
    '--with-64-bit-indices=1',
    '--with-scalar-type=real',
    '--with-shared-libraries=1',
    '--download-fblaslapack=1',
    '--download-mpich=1',
    '--with-python=1',
    '--with-debugging=0',
    '--PETSC_ARCH=arch-gxx64-real-O'
    ]
  configure.petsc_configure(configure_options)
