import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cubix",
    version="0.0.1",
    author="Martin Campos",
    author_email="tinotinocampos@gmail.com",
    description="Persistent homology for data clouds using KDE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/doctorfields/Cubex",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
