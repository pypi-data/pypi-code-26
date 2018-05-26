import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cfgur",
    version="0.1.2",
    download_url = 'https://github.com/Brayyy/cfgur-py/tarball/0.1.2',
    author = 'Bray Almini',
    author_email = 'bray@coreforge.com',
    description = 'Load environment vars, and command line arguments in a predictable, standardized way',
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    url = 'https://github.com/Brayyy/cfgur-py',
    packages=setuptools.find_packages(),
    keywords = ['environment', 'arguments', 'env', 'args'],
    classifiers=(
        "Programming Language :: Python :: 2.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
