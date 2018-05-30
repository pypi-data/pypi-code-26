import setuptools

with open("README", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flexsm",
    version="0.0.2",
    author="David Jablonski",
    author_email="dayjaby@gmail.com",
    description="A flexible state machine for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dayjaby/flexsm",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
