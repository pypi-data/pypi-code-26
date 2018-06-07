from setuptools import setup  ,find_packages
import yxspkg
from pip._internal import main as _main
import sys


def install_(module):
    args = ['install',module,'-U','--user']
    _main(args)


def run_install():
    if sys.argv[1] == 'sdist':
        return ''
    install_modules = ['lxml', 'pandas', 'bs4', 'requests', 'PyQt5', 'imageio', 'rsa', 'scipy', 'matplotlib', 'opencv-python',
                       'tushare', 'lulu', 'yxspkg_encrypt', 'yxspkg_tecfile', 'yxspkg_wget', 'lulu', 'ipython', 'sklearn',
                       'yxspkg_songzgif', 'tensorflow', 'keras', 'pyinstaller']
    module_name = {'pyinstaller': 'PyInstaller', 'opencv-python': 'cv2',
                   'ipython': 'IPython'}
    for i in install_modules:
        try:
            exec('import '+module_name.get(i, i))
        except:
            print('install ', i)
            install_(i)
    for i in install_modules:
        try:
            exec('import '+module_name.get(i, i))
        except:
            print(i, 'failed to install')
    return ''

setup(name='yxspkg',   
      version=yxspkg.__version__,    
      description='My pypi module',    
      author='Blacksong'+run_install() ,    
      author_email='blacksong@yeah.net',       
      url='https://github.com/blacksong',
      packages=find_packages(), 
      classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
)   
