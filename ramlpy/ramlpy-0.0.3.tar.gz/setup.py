from typing import List

from setuptools import setup, find_packages

import ramlpy as module


def load_requirements(fname) -> List[str]:
    """ Load requirements from a pip requirements file """
    line_iter = (line.strip() for line in open(fname))
    return [line for line in line_iter if line and not line.startswith("#")]


setup(
    name='ramlpy',
    version=module.__version__,
    author=module.__author__,
    author_email=module.__email__,
    license=module.__license__,
    description=module.__doc__,
    long_description=open('README.md').read(),
    platforms="all",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: Microsoft',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Internet',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
    ],
    packages=find_packages(exclude=['tests']),
    python_requires=">3.4.*, <4",
    install_requires=[
        'pyyaml>=3.12'
    ],
    extras_require={
        'develop': [
            'pytest'
        ],
    },
)
