import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="freshservice-wrapper",
    version="1.1",
    author="Lennart Weiss",
    author_email="lennart.weiss@egym.de",
    description="An API wrapper for Freshservice",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/egym-com/freshservice-wrapper/",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
)
