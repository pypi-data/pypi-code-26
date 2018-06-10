from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="pyATC",
    version="1.0.5",
    author="Andreas Thiele",
    author_email="andreasthiele@outlook.com",
    description="Library for working with Alivecor ATC files",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Thiele/pyatc/',
    license='MIT',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    keywords='ATC alivecor edf json',
    packages=find_packages(),
    install_requires=["python-dateutil"],
    project_urls={
        'Bug Reports': 'https://github.com/Thiele/pyatc/issues'
    }
)
