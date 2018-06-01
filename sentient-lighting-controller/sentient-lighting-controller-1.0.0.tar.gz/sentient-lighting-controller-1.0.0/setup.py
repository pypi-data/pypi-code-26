import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sentient-lighting-controller",
    version="1.0.0",
    author="Sentient Control Systems",
    author_email="levi@sentientcontrolsystems.com",
    description=("Sentient lighting controller software for the SainSmart-16 relay"),
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
