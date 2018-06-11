import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="robosim",
    version="0.1",
    author="Lukasz Zmudzinski",
    author_email="lukasz@zmudzinski.me",
    description="A pygame robotics simulator.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lukzmu/robosim",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)