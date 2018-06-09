import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='qdbd',
    version='0.0.1',
    author='High Summit LLC',
    author_email='contact@hsllc.co',
    maintainer_email='adamtwalsh@gmail.com',
    description='SQLAlchemy model generator for https://www.quickdatabasediagrams.com',
    long_description=long_description,
    classifiers=(
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License'
    )
)
