from setuptools import find_packages
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="omniidl",
    version="4.2.2",
    author="Kevin Kuehler, Tommy Yuan",
    author_email="Kevin.Kuehler@viasat.com, Tommy.Yuan@viasat.com",
    description="omniidl library for writing backends",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="LGPLv2.1",
    keywords="omniidl omniiorb corba orb",
    url="http://omniorb.sourceforge.net/",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
    ],
)
