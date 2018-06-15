import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="powpy",
    version="0.1.0",
    author="Pinneaple6",
    author_email="",
    description="A simple proof of work using SHA-256 hashes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Pineapple6/powpy",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)