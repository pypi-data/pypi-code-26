import os

from src.core.Module import Module, downloadFile, uncompressArchive, CommandWheel, runCmdHide


class JBToolbox(Module):

    url = 'https://download.jetbrains.com/toolbox/jetbrains-toolbox-1.8.3868.tar.gz'

    def __init__(self):
        super(JBToolbox, self).__init__()

    def name(self):
        return 'jbtoolbox'

    def requirements(self):
        return ['curl']

    def version(self):
        return '3.11.3'

    def info(self):
        return 'A control panel for your tools and projects'

    def author(self):
        return 'Jetbrains'

    def install(self, options):
        cw = CommandWheel()

        toDL = options.dl + '__' + self.name() + '_' + self.version() + '.tar.gz'
        toUNTAR = options.extract + '__' + self.name() + '_' + self.version() + '/'

        mydir = os.getcwd()

        cw.add('dl', downloadFile, self.url, toDL)
        cw.add('uncompress', uncompressArchive, toDL, toUNTAR)
        cw.addNoCheck('changedir', os.chdir, toUNTAR + 'jetbrains-toolbox-1.8.3868/')
        cw.add('run', runCmdHide, './jetbrains-toolbox')
        cw.addNoCheck('changedir', os.chdir, mydir)

        ret = cw.run()
        return ret

    def uninstall(self, options):
        os.system('apt remove cmake')

    def verify(self, options):
        return super(JBToolbox, self).verify(options)

    def upgrade(self, options):
        pass


def get():
    return JBToolbox()
