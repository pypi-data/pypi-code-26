import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pg_cnab240",
    version="1.0.3",
    author="Banco de Formaturas",
    author_email="alamo.saravali@bancodeformaturas.com.br",
    description="A CNAB 240 Package to process Bank payment shipping files and return files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BancoDeFormaturas/python-pg-cnab240",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
