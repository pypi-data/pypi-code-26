from setuptools import setup, find_packages

setup(
    name='p1-indexer',
    packages=find_packages(),
    version='0.2.34601063',
    description='A package for indexer algolia',
    author='Dekoruma',
    author_email='hello@dekoruma.com',
    install_requires=[
        'algoliasearch>=1.11',
        'Django>=1.9.2',
        'django-rq>=0.9.4'
    ],
    url='https://github.com/jekidekoruma/p1-indexer',  # use the URL to the github repo
)
