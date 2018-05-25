import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="vinayak",
    version="0.0.2",
    author="Vinayak Kaniyarakkal",
    author_email="vinayak.programmer@gmail.com",
    description="Just a project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vinayak-kaniyarakkal/vinayak",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
