from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
import os

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        develop.run(self)

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        os.system('jupyter notebook --generate-config')
        install.run(self)        

setup(
    name='tbsh',    # This is the name of your PyPI-package.
    version='0.2.8',                          # Update the version number for new releases    
    author="Sriharsha Sammeta",
    author_email="sriharsha4444@icloud.com",
    description='The funniest joke in the world',
    url='http://github.com/storborg/funniest',
    license='MIT',
    packages=['tbsh'],    
    install_requires=[
        'jupyter',
    ]
)
