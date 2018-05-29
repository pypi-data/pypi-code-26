from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='vapps',
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='1.1.5',

    description='A command line client for executing va_master api commands. ',
    long_description=long_description,
    long_description_content_type = 'text/markdown', 
    # The project's main homepage.
    url='https://github.com/pypa/sampleproject',

    # Author details
    author='Nikola Dokoski',
    author_email='nikola.dokoski@vapour-apps.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],

    # What does your project relate to?
    keywords='VapourApps',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
#    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    packages = ['va_client'],

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
#    py_modules=["va_api", "va_client_utils"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['requests'],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'vapps=va_client:main',
        ],
    },
)
