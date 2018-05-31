from setuptools import setup, find_packages
from os import path
import sys
here = path.abspath(path.dirname(__file__))


if sys.version_info[0]>2:
  with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
else:    
  with open(path.join(here, 'README.rst')) as f:  
    long_description = f.read().decode("UTF-8")

setup_defaults = {  
   'name'        : 'fc_bench',
   'description' : 'The fc_bench package ...',
   'version'     : '0.0.3',
   'url'         : 'http://www.math.univ-paris13.fr/~cuvelier/software/Python/fc-bench.html',
   'author'      : 'Francois Cuvelier',
   'author_email': 'cuvelier@math.univ-paris13.fr',
   'license'     : 'BSD',
   'classifiers':['Topic :: Scientific/Engineering'],
   } 

setup(name=setup_defaults['name'],
      description = setup_defaults['description'],
      long_description=long_description,
      version=setup_defaults['version'],
      url=setup_defaults['url'],
      author=setup_defaults['author'],
      author_email=setup_defaults['author_email'],
      license = setup_defaults['license'],
      platforms=["Linux", "Mac OS-X", 'Windows'],
      packages=find_packages('src'),  # include all packages under src
      package_dir={'':'src'},   # tell distutils packages are under src
      classifiers=setup_defaults['classifiers'],
      install_requires=['scipy', 'fc_tools >= 0.0.16'],
     )
