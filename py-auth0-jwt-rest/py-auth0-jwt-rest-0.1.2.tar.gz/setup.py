from distutils.core import setup
from setuptools import find_packages

setup(
    name='py-auth0-jwt-rest',
    version='0.1.2',
    url='https://github.com/hms-dbmi/py-auth0-jwt-rest',
    author='HMS DBMI Tech-core',
    author_email='dbmi-tech-core@hms.harvard.edu',
    packages=['pyauth0jwtrest',],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    install_requires=[
        'django>=1.10.0',
        'djangorestframework>=1.9.0',
        'djangorestframework-jwt>=1.7.2',
        'cryptography',
        'requests']
)
