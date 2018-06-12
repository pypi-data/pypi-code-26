import sys
from setuptools import find_packages
from setuptools.command.install import install
import subprocess
# Python 2 install
if sys.version_info[0] >= 3:
    from distutils.core import setup
else:
    from setuptools import setup


# TODO -> when ssh2-python 0.14.1 is release, switch to regular pip install
class SSH2LibInstall(install):
    def run(self):
        command = 'git clone --recursive https://github.com/ParallelSSH/ssh2-python.git'
        process = subprocess.Popen(command, shell=True, cwd='.')
        process.wait()

        build = 'git checkout a8e0d5d5da7dfd00346628b01ca07c61a5e4de1c' \
                '&& sudo ./ci/install-ssh2.sh'
        process = subprocess.Popen(build, shell=True, cwd='ssh2-python')
        process.wait()
        install.run(self)


with open('README.rst') as r_file:
    long_description = r_file.read()

setup(
    name='mig-utils',
    version='0.1.6',
    long_description=long_description,
    description='Minimum Intrusion Grid (MiG) Utilities library',
    url='https://github.com/rasmunk/mig_utils',
    author='Rasmus Munk',
    author_email='munk1@live.dk',
    packages=find_packages(),
    install_requires=[
        'fs.sshfs>=0.8.0',
        'fs>=2.0.7',
        'six>=1.10',
    ],
    cmdclass={'install': SSH2LibInstall},
    include_package_data=True,
    tests_require=[
        'pytest',
    ]
)
