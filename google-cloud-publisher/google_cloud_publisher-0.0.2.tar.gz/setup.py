import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

REQUIRED_PACKAGES = [
    'google-api-python-client==1.6.7',
]

setuptools.setup(
    name="google_cloud_publisher",
    version="0.0.2",
    author="Ivan Parra",
    author_email="ivantrips1@gmail.com",
    description="Publish to Google Cloud PubSub from App Engine Standard",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ivantrips/google_cloud_publisher",
    install_requires=REQUIRED_PACKAGES,
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),




)
