import setuptools
import dotme


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dotme",
    version=dotme.__version__,
    author="Xinhang Liu",
    author_email="xhliume@gmail.com",
    description="A dotfiles manager",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ),
)