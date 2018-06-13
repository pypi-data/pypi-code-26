import setuptools

setuptools.setup(
    name = 'sripipeline',

    version = '0.1.0',

    description = 'A package to help management and running of D3M pipelines.',

    maintainer_email = 'eaugusti@ucsc.edu',
    maintainer = 'Eriq Augustine',

    # The project's main homepage.
    url = 'https://gitlab.datadrivendiscovery.org/eaugustine/sri-pipeline',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        'Programming Language :: Python :: 3.6'
    ],

    packages = setuptools.find_packages(exclude = ['contrib', 'docs', 'tests']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires = [
        'd3m', 'networkx'
    ],

    python_requires = '>=3.6'
)
