from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='jamaddr27',
    version='0.4.0',
    packages=find_packages(),
    url='https://github.com/talbiston/jamaddr27.git',
    license='MIT',
    author='Jamison Emilio & Todd Albiston',
    author_email='foxtrot711@gmail.com',
    description='IP Subnet package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=(
        "Programming Language :: Python :: 2 ",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
