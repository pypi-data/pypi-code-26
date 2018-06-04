import setuptools

with open("README.md", "r") as file:
    longDesc = file.read()

setuptools.setup(
    name="pyConvertGUI",
    version="0.0.3",
    author="Henning Arvid Ladewig",
    author_email="anne@opentrash.com",
    description=".py to .exe converter",
    long_description=longDesc,
    long_description_content_type="text/markdown",
    url="https://github.com/letsCodeMyLife/convertPy",
    packages=setuptools.find_packages()
)
