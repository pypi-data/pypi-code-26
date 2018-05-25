import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cryptolib",
    version="0.0.2",
    author="Nguyen Truong Long",
    author_email="contact@nguyentruonglong.net",
    description="The CryptoLib module provides a set of cryptographic functions in Python",
    long_description="The CryptoLib module provides a set of cryptographic functions in Python",
    long_description_content_type="text/markdown",
    url="https://cryptolib-python.io",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ),
)