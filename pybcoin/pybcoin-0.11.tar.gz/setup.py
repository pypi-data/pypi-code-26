import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name='pybcoin',
    version='0.11',
    description='Bitcoin Trend Forecast',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Pushottam Shivraj',
    author_email='pshivraj@uw.edu',
    url='https://github.com/rguptauw/pybcoin',
    keywords=['testing', 'Forecasting', 'Timeseries'],
    packages=setuptools.find_packages(),
    classifiers=("Programming Language :: Python :: 3",),
)
