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
        install.run(self)
        os.system('juoyter notebook --generate-config')

setup(
    name='tbsh',    # This is the name of your PyPI-package.
    version='0.2.6',                          # Update the version number for new releases    
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
