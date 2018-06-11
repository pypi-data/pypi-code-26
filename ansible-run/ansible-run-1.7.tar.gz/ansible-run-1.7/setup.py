
from subprocess import check_call
from setuptools import setup
from setuptools.command.install import install
import os


class PostInstallCommand(install):
    def run(self):
        install.run(self)
        cwd = os.path.dirname(os.path.realpath(__file__))
        print("Installing to %s from %s (%s) " % (self.install_lib, self.install_scripts, cwd))
        check_call("cp %s/ansible-run %s/" % (self.install_lib, self.install_scripts), shell=True)


setup(
    name = 'ansible-run', version = '1.7',
    url = 'https://www/github.com/moshloop/ansible-run',
    author = 'Moshe Immerman', author_email = 'firstname.surname@gmail.com',
    cmdclass={'install': PostInstallCommand }
    )