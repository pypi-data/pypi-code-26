import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="statworks",
    version="0.0.1",
    author="Christophe Van Dijck",
    author_email="christophe.vdijck@gmail.com",
    description="Statworks is a library for professionals, who aren't statisticians, "
                "that want to use statistics in their daily work.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/christophevd/statworks",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)