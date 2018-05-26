from setuptools import setup, find_packages
from prala.common.common import getSetupIni

sp=getSetupIni()

setup(
      name=sp['name'],
      version=sp['version'],
      description='Practice Language',
      long_description="Practice Language",	#=open('README.md', encoding="utf-8").read(),
      url='http://github.com/dallaszkorben/prala',
      author='dallaszkorben',
      author_email='dallaszkorben@gmail.com',
      license='MIT',
      classifiers =[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
      ],
      packages = find_packages(),
      setup_requires=["pyqt5", "numpy", "pyttsx3", 'configparser', 'iso639==0.1.4'],
      install_requires=["pyqt5", 'numpy','pyttsx3', 'configparser', 'iso639==0.1.4' ],
      entry_points = {
        'console_scripts':
                ['pracon=prala.console:main', 'pragui=prala.gui:main']
      },
      package_data={
        'prala': ['templates/*.dict'],
        'prala': ['images/*.png'],
        'prala': ['common/*setup.ini'],
        'prala': ['locales/*/LC_MESSAGES/*.mo']
      },
      include_package_data = True,
      zip_safe=False)