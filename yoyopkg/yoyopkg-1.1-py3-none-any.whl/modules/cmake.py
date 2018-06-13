import os

from src.core.Module import Module, downloadFile, uncompressArchive, runCmd, CommandWheel


class Cmake(Module):

    url = 'https://cmake.org/files/v3.11/cmake-3.11.3.tar.gz'

    def __init__(self):
        super(Cmake, self).__init__()

    def name(self):
        return 'cmake'

    def requirements(self):
        return ['curl', 'make', 'g++']

    def version(self):
        return '3.11.3'

    def info(self):
        return 'CMake is an open-source, cross-platform family of tools designed to build, test and package software.'

    def author(self):
        return 'Kitware'

    def install(self, options):
        cw = CommandWheel()

        toDL = options.dl + '__' + self.name() + '_' + self.version() + '.tar.gz'
        toUNTAR = options.extract + '__' + self.name() + '_' + self.version() + '/'

        mydir = os.getcwd()

        cw.add('dl', downloadFile, self.url, toDL)
        cw.add('uncompress', uncompressArchive, toDL, toUNTAR)
        cw.addNoCheck('changedir', os.chdir, toUNTAR + 'cmake-3.11.3/')
        if options.isLocal:
            cw.add('configure', runCmd, './configure --prefix=' + options.install)
        else:
            cw.add('configure', runCmd, './configure')

        cw.add('make', runCmd, 'make')
        cw.add('make', runCmd, 'make install')
        cw.addNoCheck('changedir', os.chdir, mydir)

        ret = cw.run()
        return ret

    def uninstall(self, options):
        os.system('apt remove cmake')

    def verify(self, options):
        return super(Cmake, self).verify(options)

    def upgrade(self, options):
        pass


def get():
    return Cmake()
