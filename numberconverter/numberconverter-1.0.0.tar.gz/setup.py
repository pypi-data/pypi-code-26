import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="numberconverter",
    version="1.0.0",
    author="Mahfuz Ahmed",
    author_email="mahfuzcmt@gmail.com",
    description="numberconverter is created for converting english number to bangla number or reverse",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mahfuzcmt/engtobngnum",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)