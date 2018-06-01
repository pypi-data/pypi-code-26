from os import path

from setuptools import (
    find_packages,
    setup,
)

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='jsonpointer-helpers',
    version='0.1.0',
    description='JSON Pointer helpers',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Nikita Grishko',
    author_email='gr1n@protonmail.com',
    url='https://github.com/Gr1N/jsonpointer-helpers',
    packages=find_packages(exclude=(
        'tests.*',
        'tests',
    )),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='json jsonpointer rfc6901',
    project_urls={
        'Bug Reports': 'https://github.com/Gr1N/jsonpointer-helpers/issues',
        'Source': 'https://github.com/Gr1N/jsonpointer-helpers',
    }
)
