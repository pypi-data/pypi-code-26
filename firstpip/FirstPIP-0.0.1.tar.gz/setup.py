import setuptools

with open("README.md","r") as fh:
    long_description=fh.read()

setuptools.setup(
    name="FirstPIP",
    version="0.0.1",
    author="Seeni",
    author_email="seeni0424@gmail.com",
    long_description_content_type="text/markdown",
    url="https://github.com/Seenivasanseeni/FirstPIP",
    packages=setuptools.find_packages()
)