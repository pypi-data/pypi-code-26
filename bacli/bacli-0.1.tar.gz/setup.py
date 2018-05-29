import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bacli",
    version="0.1",
    author="Joey De Pauw",
    author_email="joeydepauw@gmail.com",
    description="Born Again Command Line Interface.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/JoeyDP/bacli',
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)