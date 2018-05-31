from setuptools import setup

setup(
    name='defpi',
    version='18.05.03',
    description='Python module for dEF-Pi',
    long_description='Python library for the dEF-Pi platform, to be used to create python services that are able to communicate with other services in the environment.',
    author='Maarten Kollenstart',
    author_email='maarten.kollenstart@tno.nl',
    install_requires=['protobuf', 'pyxb', 'requests'],
    python_requires='~=3.5',
    packages=["defpi", "defpi.common", "defpi.protobufs"]
)
