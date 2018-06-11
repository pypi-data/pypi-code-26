from setuptools import find_packages
from setuptools import setup


try:
    README = open('README.md').read() + '\n\n' + open('CHANGELOG.md').read()
except IOError:
    README = None

setup(
    name='guillotina_batch',
    version='1.0.0',
    description='batch endpoint for guillotina',
    long_description=README,
    long_description_content_type='text/markdown',
    install_requires=[
        'guillotina>=2.1.5'
    ],
    author='Nathan Van Gheem',
    author_email='vangheem@gmail.com',
    url='https://github.com/guillotinaweb/guillotina_batch',
    packages=find_packages(exclude=['demo']),
    include_package_data=True,
    extras_require={
        'test': [
            'pytest<=3.1.0',
            'docker',
            'backoff',
            'psycopg2',
            'pytest-asyncio>=0.8.0',
            'pytest-aiohttp',
            'pytest-cov',
            'coverage==4.0.3',
            'pytest-docker-fixtures',
            'asyncpg==0.15.0'
        ]
    },
    classifiers=[],
    entry_points={
    }
)
