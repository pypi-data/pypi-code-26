import os

from src.core.Module import Module, runCmd, CommandWheel, gitClone


class i3gaps(Module):

    url = 'https://www.github.com/Airblader/i3'

    def __init__(self):
        super(i3gaps, self).__init__()

    def name(self):
        return 'i3gaps'

    def requirements(self):
        return ['git', 'i3']

    def version(self):
        return '1'

    def info(self):
        return 'This is a fork of i3wm, a tiling window manager for Linux. It includes a few additional features.'

    def author(self):
        return 'Airblader'

    def install(self, options):
        cw = CommandWheel()

        mydir = os.getcwd()

        cw.add('dl', gitClone, self.url, options.dl + 'i3-gaps')
        cw.addNoCheck('changedir', os.chdir, options.dl + 'i3-gaps')
        cw.add('autoreconf', runCmd, 'autoreconf --force --install')
        cw.add('rm build', runCmd, 'rm -rf build/')
        cw.add('create build', runCmd, 'mkdir -p build')
        cw.addNoCheck('changedir', os.chdir, 'build')

        if options.isLocal:
            cw.add('autoreconf', runCmd, '../configure --prefix=' + options.install + ' --sysconfdir=/etc --disable-sanitizers')
        else:
            cw.add('autoreconf', runCmd, '../configure --prefix=/usr --sysconfdir=/etc --disable-sanitizers')

        cw.add('make', runCmd, 'make')

        if options.isLocal:
            cw.add('install', runCmd, 'make install')
        else:
            cw.add('install', runCmd, 'sudo make install')

        cw.addNoCheck('changedir', os.chdir, mydir)
        ret = cw.run()
        return ret

    def uninstall(self, options):
        return False

    def verify(self, options):
        return super(i3gaps, self).verify(options)

    def upgrade(self, options):
        pass


def get():
    return i3gaps()
