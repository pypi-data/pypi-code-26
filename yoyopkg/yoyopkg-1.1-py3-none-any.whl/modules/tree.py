import os

from src.core.Module import Module, gitClone, runCmd, CommandWheel


class Tree(Module):

    url = 'https://github.com/nodakai/tree-command.git'

    def __init__(self):
        super(Tree, self).__init__()

    def name(self):
        return 'tree'

    def requirements(self):
        return ['git', 'make', 'g++']

    def version(self):
        return '1'

    def info(self):
        return 'This is a handy little utility to display a tree view of directories that I wrote some time ago and just added color support to.'

    def author(self):
        return 'nodakai'

    def install(self, options):

        cw = CommandWheel()

        mydir = os.getcwd()

        cw.addNoCheck('changedir', os.chdir, options.dl)
        cw.add('dl', gitClone, self.url, self.name() + '_' + self.version(), options.useCached)
        cw.addNoCheck('changedir', os.chdir, self.name() + '_' + self.version())
        cw.add('make', runCmd, 'make')
        if options.isLocal:
            cw.add('install', runCmd, 'cp tree ' + options.install)
        else:
            cw.add('install', runCmd, 'sudo make install')

        cw.addNoCheck('changedir', os.chdir, mydir)

        ret = cw.run()
        return ret

    def uninstall(self, options):
        os.system('apt remove tree')

    def verify(self, options):
        return super(Tree, self).verify(options)

    def upgrade(self, options):
        pass


def get():
    return Tree()
