from distutils.core import setup

setup(
    name = 'BranchBound',
    packages = ['BranchBound'],
    version = '0.1.6',  # Ideally should be same as your GitHub release tag varsion
    description = 'Utility for reducing practical runtime in NP problems',
    author = 'John Skeet',
    author_email = 'jskeet314@gmail.com',
    url = 'https://github.com/jskeet314/branch_bound_helper',
    download_url = 'https://github.com/jskeet314/branch_bound_helper/archive/0.1.6.tar.gz',
    keywords = ['branch', 'bound'],
    classifiers = [],
)

print("running stup!")

# from setuptools import setup, find_packages  # Always prefer setuptools over distutils
# from codecs import open  # To use a consistent encoding
# from os import path
# 
# with open("README.md", "r") as fh:
#     long_description = fh.read()
# 
# setup(
#     name="branch_bound",
#     version="0.0.1",
#     author="John Skeet",
#     author_email="jskeet314@gmail.com",
#     description="A small example package",
#     long_description=long_description,
#     long_description_content_type="text/markdown",
#     url="https://github.com/jskeet314/branch_bound_helper",
#     packages=find_packages(),
#     classifiers=(
#         "Programming Language :: Python :: 3",
#         "License :: OSI Approved :: MIT License",
#         "Operating System :: OS Independent",
#     ),
# )
