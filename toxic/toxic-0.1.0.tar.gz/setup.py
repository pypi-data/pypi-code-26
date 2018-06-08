from __future__ import absolute_import, division, print_function

import sys

from setuptools import find_packages, setup

# Find package version.
for line in open('toxic/__init__.py'):
    if line.startswith('__version__ = '):
        version = line.strip().split()[2][1:-1]

# Convert README.md to rst for display at pypi (TODO)
# When releasing on pypi, make sure pandoc is on your system:
# $ brew install pandoc          # OS X
# $ sudo apt-get install pandoc  # Ubuntu Linux
try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError, OSError) as e:
    sys.stderr.write('Failed to convert README.md to rst:\n  {}\n'.format(e))
    sys.stderr.flush()
    long_description = open('README.md').read()

# Remove badges since they will always be obsolete.
blacklist = ['Build Status',
             'LICENSE',
             'Latest Version',
             'travis-ci.org',
             'pypi.python.org']

long_description = '\n'.join(
    [line for line in long_description.split('\n')
     if not any(patt in line for patt in blacklist)])

setup(
    name='toxic',
    version=version,
    description='TODO',
    long_description=long_description,
    packages=find_packages(exclude=('tests*',)),
    url='https://github.com/KakaoBrain',
    author='KakaoBrain',
    author_email='kwk236@nyu.edu',
    install_requires=[
        'numpy>=1.7',
        'scipy>=0.19.0',
        'torch',
        'six>=1.10.0',
    ],
    extras_require={
        'notebooks': ['jupyter>=1.0.0'],
        'visualization': [
            'matplotlib>=1.3',
            'visdom>=0.1.4',
            'pillow',
        ],
        'test': [
            'pytest',
            'pytest-cov',
            'nbval',
            'visdom',
            'torchvision',
        ],
        'profile': ['prettytable'],
        'dev': [
            'torchvision',
            'flake8',
            'yapf',
            'isort',
            'pytest',
            'pytest-xdist',
            'nbval',
            'nbstripout',
            'pypandoc',
            'sphinx',
            'sphinx_rtd_theme',
        ],
    },
    tests_require=['flake8', 'pytest'],
    keywords='machine learning security adversarial attack'
             'defense deep learning pytorch',
    license='MIT License',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3.4',
    ],
    # yapf
)
