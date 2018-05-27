import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="crycompare",
    version="1.2",
    author="Stefan Stojanovic",
    author_email="stefs304@gmail.com",
    description="Python wrapper for CryptoCompare public API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stefs304/cryCompare",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)