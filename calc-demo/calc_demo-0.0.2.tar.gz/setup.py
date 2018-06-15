import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="calc_demo",
    version="0.0.2",
    author="Waldirio",
    author_email="waldirio@gmail.com",
    description="A small calc example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/waldirio/calc_demo",
    packages=setuptools.find_packages(),
    scripts=['bin/calc_demo'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
