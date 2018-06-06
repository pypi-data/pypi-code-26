import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py_pushover_simple",
    version="0.1.1",
    author="Matthew Jorgensen",
    author_email="matthew@jrgnsn.net",
    description="A wrapper for sending push notifications with Puhsover",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/matthewjorgensen/py_pushover_simple",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
