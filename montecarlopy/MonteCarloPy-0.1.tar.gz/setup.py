import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MonteCarloPy",
    version="0.1",
    author="Roshan J Mehta",
    author_email="sonicroshan122@gmail.com",
    description="PyMonteCarlo is a module that has helper function for monte carlo simulations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SonicRoshan/PyMonteCarlo",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)