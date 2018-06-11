from setuptools import setup, find_packages

setup(
    name = 'admiral',
    description = "Simple python high-performance computing cluster batch submission",
    version = '0.2',

    author = "Noah Spies",
    url = "https://github.com/nspies/admiral",
    
    packages = find_packages('src'),
    package_dir = {"": "src"},

    install_requires = ["humanfriendly"]

)
