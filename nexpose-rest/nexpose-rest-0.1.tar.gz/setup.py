import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nexpose-rest",
    version="0.1",
    author="Patrick Pirker",
    author_email="pypi@patralos.at",
    description="Basic inofficial implementation of the nexpose rest api",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Patralos/nexpose-rest/",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
