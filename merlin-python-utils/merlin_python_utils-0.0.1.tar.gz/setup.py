import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

REQUIRED_PACKAGES = [
    "Flask==1.0.2",
    "google-api-python-client==1.7.3",
    "google-auth==1.5.0",
    "requests==2.18.4",
    "oauth2client==4.1.2",
]

setuptools.setup(
    name="merlin_python_utils",
    version="0.0.1",
    author="Merlin Jobs inc.",
    author_email="oficina@merlinjobs.com",
    description="Merlin utils",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://http//github.com/merlinapp/merlin_python_utils",
    install_requires=REQUIRED_PACKAGES,
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
