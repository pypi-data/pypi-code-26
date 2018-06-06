import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="swiftai",
  version="0.1",
  author="Aakash N S",
  author_email="opensource@swiftace.ai",
  description="Utilities and helper functions for Pytorch and FastAI deep learning libraries",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/aakashns/swiftai",
  packages=setuptools.find_packages(),
  classifiers=(
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ),
)