from setuptools import setup, find_packages

setup(
    name='myFirstPackage_TrialGuyOne',
    version='0.1.0.dev4',
    packages=find_packages(exclude=['tests*']),
    install_requires=['numpy'],
    description='A Simple Python Package for studying and Learning Python',
    author='Trial Man',
    url='https://gitlab.com/TheOnlyTrialMan/TheFirstPythonPackage.git',

)