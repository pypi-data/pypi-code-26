from setuptools import setup, find_packages

setup(
    name='airlib',  # Required
    version='1.0.0',  # Required
    description='A airlib sample Python project',  # Required
    author='air lee',  # Optional

    packages=find_packages(),  # Required
    include_package_data = True,
    platforms = 'any',
    install_requires=[],  # Optional

    )
