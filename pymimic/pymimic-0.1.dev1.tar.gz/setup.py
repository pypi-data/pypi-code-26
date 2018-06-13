import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymimic",
    version="0.1.dev1",
    author="Amery Gration",
    author_email="alg26@le.ac.uk",
    description="A pure-Python implementation of Gaussian-process emulation and efficient global optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AmeryGration/pymimic",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
