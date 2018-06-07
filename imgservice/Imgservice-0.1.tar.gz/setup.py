import os
from setuptools import setup, find_packages

version = '0.1'

here = os.path.dirname(__file__)

with open(os.path.join(here, 'README.rst')) as fp:
    longdesc = fp.read()

with open(os.path.join(here, 'CHANGELOG.rst')) as fp:
    longdesc += "\n\n" + fp.read()


setup(
    name='Imgservice',
    version=version,
    packages=find_packages(),
    url='https://github.com/rshk/imgservice2',
    license='BSD License',
    author='Samuele Santi',
    author_email='samuele.santi@reinventsoftware.io',
    description='Image proxy service',
    long_description=longdesc,
    install_requires=[
        'click',
        'flask',
        'flask-sslify',
        'itsdangerous',
        'requests',
        'boto3',
        'pillow',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
        'flake8',
    ],
    # test_suite='tests',
    classifiers=[
        'License :: OSI Approved :: BSD License',

        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',

        # 'Programming Language :: Python :: Implementation :: CPython',
        # 'Programming Language :: Python :: Implementation :: IronPython',
        # 'Programming Language :: Python :: Implementation :: Jython',
        # 'Programming Language :: Python :: Implementation :: PyPy',
        # 'Programming Language :: Python :: Implementation :: Stackless',
    ],
    # entry_points={
    #     'console_scripts': ['PACKAGE_NAME=PACKAGE_NAME.cli:main'],
    # },
    package_data={'': ['README.rst', 'CHANGELOG.rst']},
    include_package_data=True,
    zip_safe=False)
