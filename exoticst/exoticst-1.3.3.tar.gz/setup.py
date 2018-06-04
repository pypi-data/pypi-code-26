import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='exoticst',
    version='1.3.3',
    author='Val Giner',
    author_email='valginer0@gmail.com',
    description='Data structures, either not present in standard Python libs or are asymptotically more efficient',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/valginer0/exotic-structures.git',
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)


