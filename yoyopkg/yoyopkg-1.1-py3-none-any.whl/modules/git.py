import os

from src.core.Module import Module


class Git(Module):

    def __init__(self):
        super(Git, self).__init__()

    def name(self):
        return 'git'

    def requirements(self):
        return ['debian', 'apt']

    def version(self):
        return '1'

    def info(self):
        return 'git GNU Versioning tool'

    def author(self):
        return 'Linus Torvald'

    def install(self, options):
        os.system('apt install git')
        return True

    def uninstall(self, options):
        os.system('apt remove git')

    def verify(self, options):
        return super(Git, self).verify(options)

    def upgrade(self, options):
        pass


def get():
    return Git()
