import os

from src.core.Module import Module, gitClone, runCmdHide, CommandWheel


class Blih(Module):

    url = 'https://github.com/bocal/blih.git'

    def __init__(self):
        super(Blih, self).__init__()

    def name(self):
        return 'blih'

    def requirements(self):
        return ['git']

    def version(self):
        return '2.0'

    def info(self):
        return 'BLIH - Bocal Lightweight Interface for Humans'

    def author(self):
        return 'Emmanuel Vadot'

    def install(self, options):

        cw = CommandWheel()

        mydir = os.getcwd()

        cw.addNoCheck('changedir', os.chdir, options.dl)
        cw.add('dl', gitClone, self.url, self.name() + '_' + self.version(), options.useCached, True)
        cw.addNoCheck('changedir', os.chdir, self.name() + '_' + self.version())
        if options.isLocal:
            cw.add('setup', runCmdHide, 'python3 setup.py install --user')
        else:
            cw.add('setup', runCmdHide, 'python3 setup.py install')

        cw.addNoCheck('changedir', os.chdir, mydir)

        ret = cw.run()
        return ret

    def uninstall(self, options):
        pass
        # os.system('apt remove tree')

    def verify(self, options):
        return super(Blih, self).verify(options)

    def upgrade(self, options):
        pass


def get():
    return Blih()
