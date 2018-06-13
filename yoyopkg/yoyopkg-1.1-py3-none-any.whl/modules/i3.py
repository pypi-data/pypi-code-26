import os

from src.core.Module import Module, runCmd, CommandWheel


class i3(Module):

    url = 'https://github.com/i3/i3.git'

    def __init__(self):
        super(i3, self).__init__()

    def name(self):
        return 'i3'

    def requirements(self):
        return ['apt']

    def version(self):
        return '1'

    def info(self):
        return 'This is a tiling window manager for Linux.'

    def author(self):
        return 'i3 creator'

    def install(self, options):
        cw = CommandWheel()

        cw.add('add apt', runCmd, 'sudo /usr/lib/apt/apt-helper download-file http://debian.sur5r.net/i3/pool/main/s/sur5r-keyring/sur5r-keyring_2018.01.30_all.deb keyring.deb SHA256:baa43dbbd7232ea2b5444cae238d53bebb9d34601cc000e82f11111b1889078a')
        cw.add('apt keyring', runCmd, 'sudo apt install ./keyring.deb')
        cw.add('apt echo', runCmd, 'sudo echo \'deb http://dl.bintray.com/i3/i3-autobuild sid main\' > /etc/apt/sources.list.d/i3-autobuild.list')
        cw.add('apt update', runCmd, 'sudo apt update')
        cw.add('apt install', runCmd, 'sudo apt install i3')

        ret = cw.run()
        return ret

    def uninstall(self, options):
        os.system('sudo apt remove i3')

    def verify(self, options):
        return super(i3, self).verify(options)

    def upgrade(self, options):
        pass


def get():
    return i3()
