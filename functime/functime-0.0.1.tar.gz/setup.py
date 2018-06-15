import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="functime",
    version="0.0.1",
    author="jhyao",
    author_email="yaojinhonggg@gmail.com",
    description="Python function timing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jhyao/functime",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)