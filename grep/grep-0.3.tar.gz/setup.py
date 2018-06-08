"""Setup file for handling packaging and distribution."""
from setuptools import setup

setup(
    name="grep",
    packages=["grep"],
    version="0.03",
    description="String lookup has never been prettier.",
    author="Dan Elkis",
    author_email="elkissdan@gmail.com",
    license="MIT",
    zip_safe=False,
    url="https://github.com/rinslow/grep",
    keywords=["string", "lookup", "grep"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
