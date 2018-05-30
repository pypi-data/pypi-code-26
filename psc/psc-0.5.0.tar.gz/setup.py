from setuptools import setup
import unittest

VERSION = "0.5.0"


def default_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite


def run_test():
    test_suite = default_test_suite()
    test_suite.run()


setup(
    name='psc',
    version=VERSION,
    description='A cli credential/secret storage utility using EC2 SSM Parameter Store',
    license='MIT',
    url='https://github.com/smooch/parameter-store-client',
    author='Smooch',
    author_email='ops@smooch.io',
    scripts=['psc.py'],
    entry_points={
        'console_scripts': [
            'psc = psc:main'
        ]
    },
    py_modules=['psc'],
    install_requires=[
        'boto3>=1.7.9',
        'prettytable>=0.7.2'
    ],
    test_suite='setup.default_test_suite'
)
