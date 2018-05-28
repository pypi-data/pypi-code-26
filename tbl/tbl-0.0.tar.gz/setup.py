from setuptools import setup, find_packages

# declare these here since we use them in multiple places
_tests_require = [
    'pytest',
    'pytest-cov',
    'flake8',
]


setup(
    # package info
    name='tbl',
    description='Simple table printing for Python CLI tools',
    url='https://github.com/AstromechZA/tbl',
    author='Ben Meier',
    author_email='ben@example.com',
    packages=find_packages(exclude=['tests', 'tests.*']),

    # run time requirements
    # exact versions are in the requirements.txt file
    install_requires=[],

    # need this for setup.py test
    setup_requires=[
        'pytest-runner',
        'setuptools_scm',
    ],

    # needs this if using setuptools_scm
    use_scm_version=(lambda: dict(
        version_scheme=lambda t: str(t.tag),
        local_scheme=lambda t: '',
    )),

    # test dependencies
    tests_require=_tests_require,
    extras_require={
        # this allows us to pip install .[test] for all test dependencies
        'test': _tests_require,
    }
)
