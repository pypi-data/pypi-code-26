from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='quickslice',
    version=1.1,
    author='Raghav Arora',
    author_email='agu94.raghav@gmail.com',
    url='http://github.com/raghavaro/quickslice',
    description="Extract slices from compressed volumetric data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    packages=find_packages(),
    scripts=['quickslice'],
    install_requires=[
        'Pillow==5.1.0',
        'numpy==1.14.3'
    ],
    classifiers=(
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)