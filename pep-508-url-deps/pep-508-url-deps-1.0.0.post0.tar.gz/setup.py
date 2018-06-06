from textwrap import dedent
from setuptools import setup, find_packages

setup(
    name="pep-508-url-deps",
    version="1.0.0.post0",
    description="A package with a PEP 508 URL dependency.",
    long_description=dedent("""
        This package is used for ensuring that pip refuses to install a
        URL-based dependency for a package that it fetches from PyPI.
    """).strip(),
    install_requires=[
        "sampleproject @ https://github.com/pypa/sampleproject/archive/master.zip"
    ],

    # I added this file because why not.
    py_modules=["magic_cat"],
)
