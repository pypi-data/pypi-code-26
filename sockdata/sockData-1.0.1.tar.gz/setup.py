import setuptools

with open("README.md", "r") as file:
    longDesc = file.read()

setuptools.setup(
    name="sockData",
    version="1.0.1",
    author="Henning Arvid Ladewig",
    author_email="anne@opentrash.com",
    description="Socket extension",
    long_description=longDesc,
    long_description_content_type="text/markdown",
    url="https://github.com/letsCodeMyLife/sockData/",
    packages=setuptools.find_packages()
)
