from setuptools import setup  ,find_packages
import yxspkg
from pip._internal import main as _main
import sys


def install_(module):
    args = ['install',module,'-U','--user']
    _main(args)

setup(name='yxspkg',   
      version=yxspkg.__version__,    
      description='My pypi module',    
      author='Blacksong',    
      author_email='blacksong@yeah.net',       
      url='https://github.com/blacksong',
      packages=find_packages(), 
      classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
)   
if __name__=='__main__':
    
    if sys.argv[1].strip() != 'sdist':
        install_modules=['lxml','pandas','bs4','requests','PyQt5','imageio','rsa','scipy','matplotlib','opencv-python',
        'tushare','lulu','yxspkg_encrypt','yxspkg_tecfile','yxspkg_wget','lulu','ipython',
        'yxspkg_songzgif','tensorflow','keras','pyinstaller']
        module_name = {'pyinstaller':'PyInstaller','opencv-python':'cv2'}
        for i in install_modules:
            install_(i)
        for i in install_modules:
          try:
              exec('import '+module_name.get(i,i))
          except:
              print(i,'failed to install')