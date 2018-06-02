import setuptools

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wanakana",
    version="1.0.0",
    author="Luke Casey",
    author_email="lc94dev@gmail.com",
    description="A library to assist in detecting Japanese text",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luke-c/WanaKanaPython",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: Japanese",
    ),
)
