import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pysmvr",
    version="0.0.6",
    author="Antti Varjoinen",
    author_email="antti@varjoinen.org",
    description="Commandline tool and module to handle semantic versions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/varjoinen/pysmvr.git",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    entry_points={
        'console_scripts': [
            'pysmvr = pysmvr.__main__:main',
        ],
    }
)
