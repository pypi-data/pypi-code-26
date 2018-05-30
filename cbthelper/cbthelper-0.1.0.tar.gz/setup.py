import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='cbthelper',
    version='0.1.0',
    author='Tim Hamilton',
    author_email='timh@crossbrowsertesting.com',
    description='a helper library for cross browser testing\'s selenium api',
    long_description=long_description,
    url='https://github.com/TimmyTango/hackathon2018',
    packages=setuptools.find_packages(),
    install_requires=[
        'fuzzywuzzy',
    ],
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ),
)
