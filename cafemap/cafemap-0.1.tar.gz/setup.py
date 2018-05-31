import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cafemap",
    version="0.1",
    author="Fayyaz Minhas",
    author_email="fayyazafsar@gmail.com",
    description="CAFE-Map: Context Aware Feature Mapping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/foxtrotmike/cafemap",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)