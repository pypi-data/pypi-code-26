
from subprocess import check_call
from setuptools import setup
from setuptools.command.install import install
import os
cwd = os.path.dirname(os.path.realpath(__file__))


class PostInstallCommand(install):
    def run(self):
        check_call("cp %s/ansible-run /usr/local/bin/" % cwd, shell=True)
        install.run(self)


setup(
    name = 'ansible-run', version = '1.6',
    url = 'https://www/github.com/moshloop/ansible-run',
    author = 'Moshe Immerman', author_email = 'firstname.surname@gmail.com',
    cmdclass={'install': PostInstallCommand }
    )