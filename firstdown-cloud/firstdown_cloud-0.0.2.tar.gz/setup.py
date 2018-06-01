from setuptools import setup

setup(
    name='firstdown_cloud',
    version='0.0.2',
    url='https://github.com/OpsLabJPL/firstdown_cloud',
    license='Apache 2.0',
    author='Mark Powell',
    author_email='Mark.W.Powell@jpl.nasa.gov',
    description='Python library for securely publishing JPL ops summary data to Govcloud.',
    long_description='Python library for securely publishing JPL ops summary data to Govcloud.',

    packages=['firstdown_cloud'],

    test_suite='tests',

    install_requires=['pycrypto','boto3'],

    tests_require=['moto'],

    entry_points={
        'console_scripts': [
            'fds3 = firstdown_cloud.s3:main'
        ]
    }
)
