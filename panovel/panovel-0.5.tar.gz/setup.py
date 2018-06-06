from os import path
from setuptools import setup


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='panovel',
    version='0.5',
    description='A script to make a novel out of markdown files with the help of pandoc',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/dickloraine/panovel',
    author='dloraine',
    author_email='dickloraine@gmx.net',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Text Processing',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='pandoc novel writing text conversion',

    packages=['panovel'],
    python_requires='>=3.6',
    package_data={
        'panovel': ['*.md', 'filter/*.*', 'styles/*.*', 'templates/*.*'],
    },
    install_requires=[
        'pyYaml',
        'panflute',
        'pyscss'
    ],
    entry_points={
        'console_scripts': ['panovel=panovel.main:main'],
    },
    zip_safe=False
)
