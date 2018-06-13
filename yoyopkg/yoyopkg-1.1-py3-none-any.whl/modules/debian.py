import os

from src.core.Module import Module
from src.core.log import perror


class Debian(Module):

    def __init__(self):
        super(Debian, self).__init__()

    def name(self):
        return 'debian'

    def requirements(self):
        return []

    def version(self):
        return '1'

    def info(self):
        return 'Debian'

    def author(self):
        return 'Linus Torvald'

    def install(self, options):
        perror('Debian is an OS, cant install')
        return False

    def uninstall(self, options):
        return False

    def verify(self, options):
        if os.path.isfile('/etc/debian_version'):
            return True
        return False

    def upgrade(self, options):
        return False


def get():
    return Debian()
