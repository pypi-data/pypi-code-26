""" Setup script. """

import os.path
import re
import setuptools

with open("README.rst", "r") as fh:
    LONG_DESCRIPTION = fh.read()


def get_version(path):
    path = os.path.join(os.path.dirname(__file__), path)
    with open(path) as f:
        text = f.read()
    regex = r"""^__version__ = ['"]([^'"]*)['"]"""
    match = re.search(regex, text, re.M)
    if match:
        return match.group(1)
    raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name="generic_paths",
    version=get_version(os.path.join("generic_paths", "__init__.py")),
    author="Dhoi Almeida",
    description="Generic pathfinding algorithms for Python.",
    long_description=LONG_DESCRIPTION,
    url="https://github.com/dhoialmeida/generic_paths",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
