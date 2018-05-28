from setuptools import setup, find_packages

VERSION = '0.29.1'

setup(
    name='thicket',
    version=str(VERSION),
    description='File Path API for Python.',
    packages=[
        'forest',
        'forest.ffmpeg_wrapper',
        'forest.ffmpeg_wrapper.parsers',
              ]
,
    url='https://github.com/GabrielC101/forest',
    author='Gabriel Curio',
    author_email='contactMeViaGithub@dummy.com',
    install_requires=[
        'marshmallow',
        'python-magic',
        'six',
        'xxhash'
    ],
    python_requires='>=3.5',
    keywords=['system', 'linux'],
)
