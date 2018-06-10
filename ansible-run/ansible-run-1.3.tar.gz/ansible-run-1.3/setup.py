
from subprocess import check_call
from setuptools import setup
from setuptools.command.install import install


class PostInstallCommand(install):
    def run(self):
        check_call("cp ansible-run /usr/local/bin", shell=True)
        install.run(self)


setup(
    name = 'ansible-run', version = '1.3',
    url = 'https://www/github.com/moshloop/ansible-run',
    author = 'Moshe Immerman', author_email = 'firstname.surname@gmail.com',
    cmdclass={'install': PostInstallCommand }
    )