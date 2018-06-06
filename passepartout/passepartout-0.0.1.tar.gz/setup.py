from setuptools import setup

try:
    with open('README.MD') as readme_file:
        README = readme_file.read()
except FileNotFoundError:
    README = ""

VERSION = '0.0.1'

setup(
    name='passepartout',
    packages=['passepartout'],
    version=VERSION,
    description='',
    long_description=README,
    license='MIT',
    install_requires=[
    ],
    author='Romain Moreau',
    author_email='moreau.romain83@gmail.com',
    url='https://github.com/Varkal/passepartout',
    download_url='https://github.com/Varkal/passepartout/archive/{}.tar.gz'.format(VERSION),
    keywords=['passepartout'],
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
)
