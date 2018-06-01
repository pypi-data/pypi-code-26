from setuptools import setup, find_packages

setup(
    name='woning-wattle',
    version='0.0.4',
    description='Library for converting yaml structures to Python objects, '
                'based on a predefined object hierarchy schema.',
    packages=find_packages(),
    install_requires=[
        'pyyaml'
    ]
)
