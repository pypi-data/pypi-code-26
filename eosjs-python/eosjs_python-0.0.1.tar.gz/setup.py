import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="eosjs_python",
    version="0.0.1",
    author="Raphael Gaudreault",
    author_email="raphael.gaudreault@eva.coop",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EvaCoop/eosjs_python",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)