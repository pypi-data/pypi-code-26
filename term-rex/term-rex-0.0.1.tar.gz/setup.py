import setuptools

with open("term-rex/README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="term-rex",
    version="0.0.1",
    author="Hemang Kandwal",
    author_email="hemangkandwal@gmail.com",
    description="A Terminal Based Offline T-Rex Game",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hkdeman/term-rex",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ))