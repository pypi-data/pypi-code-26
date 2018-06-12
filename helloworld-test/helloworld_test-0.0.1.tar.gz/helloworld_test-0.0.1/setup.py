import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="helloworld_test",
    version="0.0.1",
    author="matis",
    author_email="matistis1@gmail.com",
    description="A small example package",
    long_description="A small example package",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)