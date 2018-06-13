import os

from src.core.Module import Module, downloadFile, runCmd, CommandWheel


class GChrome(Module):

    url = 'https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb'

    def __init__(self):
        super(GChrome, self).__init__()

    def name(self):
        return 'gchrome'

    def requirements(self):
        return ['curl']

    def version(self):
        return '1'

    def info(self):
        return 'One fast, simple, and secure browser for all your devices.'

    def author(self):
        return 'Google'

    def install(self, options):
        cw = CommandWheel()

        toDL = options.dl + '__' + self.name() + '_' + self.version() + '.deb'

        cw.add('dl', downloadFile, self.url, toDL)
        cw.add('install', runCmd, 'sudo dpkg -i ' + toDL)

        ret = cw.run()
        return ret

    def uninstall(self, options):
        os.system('apt remove google-chrome')

    def verify(self, options):
        return super(GChrome, self).verify(options)

    def upgrade(self, options):
        pass


def get():
    return GChrome()
