import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="crycompare",
    version="1.2.1",
    author="Stefan Stojanovic",
    author_email="stefs304@gmail.com",
    description="Python wrapper for CryptoCompare public API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stefs304/cryCompare",
    packages=setuptools.find_packages(),
    install_requires=['requests',],
    classifiers=(
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
