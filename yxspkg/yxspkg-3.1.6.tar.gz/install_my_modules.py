from threading import Thread
from pip._internal import main as _main


def install_(module):
    args = ['install',module,'-U','--user']
    _main(args)
    print('ok'*100)

def main_():
    install_modules=['lxml','pandas','bs4','requests','PyQt5',
    'tushare','yxspkg_encrypt','yxspkg_tecfile','yxspkg_wget',
    'yxspkg_songzgif','tensorflow','keras','pyinstaller']
    for i in install_modules:
        install_(i)