import setuptools
import os

with open("README.md", "r") as fh:
    long_description = fh.read()
    
about = {}
with open(os.path.join('slowbreak', '__version__.py'), 'r') as f:
    exec(f.read(), about)

setuptools.setup(
    name=about['__title__'],
    version=about['__version__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    description=about['__description__'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=about['__url__'],
    packages=setuptools.find_packages(exclude=('*.test',)),
    classifiers=(
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
