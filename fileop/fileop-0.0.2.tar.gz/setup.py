import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fileop",
    version="0.0.2",
    author="Saurabh Londhe",
    author_email="saurabhlondhe1111@gmail.com",
    description="All file operations without writing code for it",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/saurabhlondhe/fileop",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
