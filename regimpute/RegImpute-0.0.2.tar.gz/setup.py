import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="RegImpute",
    version="0.0.2",
    author="Jeremy Jacobsen",
    author_email="reventropy2003@yahoo.co",
    description="Regression Based Imputation for Python",
    long_description="Iterative regression based imputation for sklean regression libraries",
    url="https://github.com/reventropy/RegImpute/",
    packages=setuptools.find_packages(),
)
