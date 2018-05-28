import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="properly_util_python",
    version="0.4.0",
    author="GoProperly",
    author_email="info@goproperly.com",
    description="Utility and helper functions for common Properly operations in python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GoProperly/properly-util-python",
    packages=setuptools.find_packages(exclude=["custom_scripts"]),
    classifiers=(
        "Programming Language :: Python :: 3",
    ),
)