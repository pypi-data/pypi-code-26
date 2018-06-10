import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pipeish",
    version="0.2.0",
    author="Andrey Elizarov",
    author_email="vigilancer@example.com",
    description="shell pipes and redirecting for python",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/vigilancer/pipeish",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved",
        "Operating System :: OS Independent",
    ),
    license="WTFPL",
)
