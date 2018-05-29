import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="metrics_tools",
    version="0.0.2",
    author="Jonnyblacklabel",
    author_email="mail@jonnyblacklabel.de",
    description="Package for making calls to metrics.tools API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jonnyblacklabel/metrics_tools",
    packages=setuptools.find_packages(),
    install_requires=['requests','jsonpickle'],
    python_requires='>=3.6',
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)