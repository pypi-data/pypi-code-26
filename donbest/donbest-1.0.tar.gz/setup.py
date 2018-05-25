import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

required = [
    'requests'
]

setuptools.setup(
    name="donbest",
    version="1.0",
    author="Matthew McManus",
    author_email="matt@rexmark.co",
    description="An easy-to-use python wrapper for the Don Best Sports API",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/mamcmanus/donbest.py",
    py_modules=['donbest'],
    install_requires=required,
    python_requires='>=3',
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)