import sys
from setuptools import setup

setup_requires = ['setuptools >= 30.3.0']
if {'pytest', 'test', 'ptr'}.intersection(sys.argv):
    setup_requires.append('pytest-runner')
if {'build_sphinx'}.intersection(sys.argv):
    setup_requires.extend(['celery_eternal>=0.0.2', 'recommonmark', 'sphinx',
                           'sphinx_celery'])

setup(setup_requires=setup_requires)
