import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="redlock-dist",
    version="1.0.0",
    author="kerol",
    author_email="ikerol@163.com",
    description="Distributed locks with Redis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kerol/redlock-dist",
    packages=setuptools.find_packages(),
    classifiers=(
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 3.6',
    ),
    install_requires=[
        'redis>=2.10.6',
    ]
)
