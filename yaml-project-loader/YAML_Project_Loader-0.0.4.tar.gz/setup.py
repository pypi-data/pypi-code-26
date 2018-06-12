import setuptools
from subprocess import check_output

version = check_output(['git', 'describe'])

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="YAML_Project_Loader",
    version="0.0.4",
    author="FAS GmbH",
    author_email="daniel.ramirez@fahrerassistenzsysteme.de",
    description="YAML Project Loader",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://fahrerassistenzsysteme.de",
    project_urls={
        "Internal Repository": "http://gogs.kse.local/ramirda/YAML_Project_Loader"
    },
    packages=setuptools.find_packages(),
    classifiers=(
        "Topic :: Utilities",
        "Topic :: Software Development :: Pre-processors",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ),
)