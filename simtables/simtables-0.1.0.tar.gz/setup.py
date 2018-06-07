import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='simtables',
    version='0.1.0',
    author='Alexander Chambers',
    author_email='alexander.chambers8472@gmail.com',
    description='Simple tables',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/achambers8472/simtables',
    packages=setuptools.find_packages(),
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ),
    # setup_requires=['pytest-runner'],
    # tests_require=['pytest'],
    # test_suite='tests',
)
