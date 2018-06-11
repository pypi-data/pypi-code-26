import re
from setuptools import setup


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('jen2jen/jen2jen.py').read(),
    re.M
    ).group(1)


with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")

setup(
    name = "jen2jen",
    packages = ["jen2jen", ""],
    entry_points = {
        "console_scripts": ['jen2jen = jen2jen.jen2jen:main']
        },
    version = version,
    description = "Python command line Jenkins cloning and backing up tool, provides methods to interact with Jenkins",
    long_description = long_descr,
    author = "Oleg 'helgie' Lymarchuk",
    author_email = "oleg.lymarchuk@gmail.com",
    url = "https://helgie.github.io/jen2jen/",
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='Jenkins jobs pipelines save clone backup build continuous deployment',
    install_requires=['docopt', 'lxml', 'pyyaml', 'requests']
)