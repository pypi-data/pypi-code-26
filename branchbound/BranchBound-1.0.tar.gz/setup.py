from distutils.core import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
import platform
import subprocess

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run_chmod(self):
        is_windows = "win" in platform.system().lower()
        if not is_windows:
            subprocess.check_call(['chmod', '+x' 'heuristic_cache/*'])
    def run(self):
        self.run_chmod()
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        develop.run(self)

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run_chmod(self):
        is_windows = "win" in platform.system().lower()
        if not is_windows:
            subprocess.check_call(['chmod', '+x' 'heuristic_cache/*'])
    def run(self):
        self.run_chmod()
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        install.run(self)

setup(
    name = 'BranchBound',
    packages = ['BranchBound'],
    version = '1.0',  # Ideally should be same as your GitHub release tag varsion
    description = 'Utility for reducing practical runtime in NP problems',
    author = 'John Skeet',
    author_email = 'jskeet314@gmail.com',
    url = 'https://github.com/jskeet314/branch_bound_helper',
    download_url = 'https://github.com/jskeet314/branch_bound_helper/archive/1.0.tar.gz',
    keywords = ['branch', 'bound'],
    classifiers = [],
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
)


# from setuptools import setup, find_packages  # Always prefer setuptools over distutils
# from codecs import open  # To use a consistent encoding
# from os import path
# 
# with open("README.md", "r") as fh:
#     long_description = fh.read()
# 
# setup(
#     name="branch_bound",
#     version="0.0.1",
#     author="John Skeet",
#     author_email="jskeet314@gmail.com",
#     description="A small example package",
#     long_description=long_description,
#     long_description_content_type="text/markdown",
#     url="https://github.com/jskeet314/branch_bound_helper",
#     packages=find_packages(),
#     classifiers=(
#         "Programming Language :: Python :: 3",
#         "License :: OSI Approved :: MIT License",
#         "Operating System :: OS Independent",
#     ),
# )
