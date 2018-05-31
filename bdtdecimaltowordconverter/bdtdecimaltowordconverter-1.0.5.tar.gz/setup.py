import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bdtdecimaltowordconverter",
    version="1.0.5",
    author="Mahfuz Ahmed",
    author_email="mahfuzcmt@gmail.com",
    description="bdtdecimaltowordconverter is created for converting decimal to word in both bangla and english in BDT format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mahfuzcmt/BanglaDecimalToWordConverter",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)