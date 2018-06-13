import setuptools


setuptools.setup(
    name="properly_util_python",
    version="0.7.1",
    author="GoProperly",
    author_email="info@goproperly.com",
    description="Utility and helper functions for common Properly operations in python.",
    long_description="public",
    long_description_content_type="text/markdown",
    url="https://github.com/GoProperly/properly-util-python",
    packages=setuptools.find_packages(exclude=["custom_scripts", "tests"]),
    classifiers=(
        "Programming Language :: Python :: 3",
    ),
)