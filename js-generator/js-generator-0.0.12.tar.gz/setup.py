import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="js-generator",
    version="0.0.12",
    author="Gal Ben Haim",
    author_email="gal_ben_haim@yahoo.com",
    description="CLI tool for creating js templates",
    long_description=long_description,
    url="https://github.com/pypa/example-project",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
