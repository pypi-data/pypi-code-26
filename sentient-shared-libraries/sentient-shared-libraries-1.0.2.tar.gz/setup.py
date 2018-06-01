import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sentient-shared-libraries",
    version="1.0.2",
    author="Sentient Control Systems",
    author_email="levi@sentientcontrolsystems.com",
    description=("Shared libraries required all Sentient monitors and "
                 "controllers"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sentient-controls/shared-libraries",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
