import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lorem-bot",
    version="0.0.1",
    author="DSW12018",
    author_email="thiagoflames@gmail.com",
    license='MIT',
    description="A bot framework for devolopers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DSW12018/LoremBot",
    packages=setuptools.find_packages(),
    classifiers=(
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        "Operating System :: OS Independent",
    ),
)

