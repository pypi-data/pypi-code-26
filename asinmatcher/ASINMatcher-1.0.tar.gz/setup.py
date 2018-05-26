from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='ASINMatcher',
    version='1.0',
    description='A project to get the product details on Amazon',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='reetikaS',
    packages=['ASINMatcher'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"]
)
