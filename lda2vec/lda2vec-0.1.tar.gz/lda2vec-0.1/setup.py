from setuptools import find_packages
from distutils.core import setup

with open("requirements.txt") as f:
	install_requires = f.read().splitlines()

setup(name="lda2vec",
	  version="0.1",
	  description="Tools for interpreting natural language",
	  author="Nathan Raw",
	  author_email="nxr9266@rit.edu",
	  install_requires=install_requires,
	  packages=find_packages("lda2vec"),
	  url="")