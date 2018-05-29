import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="primePy",
    version="1.1",
    author="Indrajit Jana",
    author_email="ijana@temple.edu",
    description="This module contains several useful functions to work with prime numbers. For example, extracting all the prime factors (with multiplicity) of a positive integer reasonably fast.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/janaindrajit/primes",
    packages=setuptools.find_packages(),
    keywords=['fast', 'prime', 'facorization'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)