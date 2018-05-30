from setuptools import setup
import aoet

setup(name='aoet',
      version=aoet.__version__,
      description='Automation of Exploratory Testing',
      url='https://gitlab.tubit.tu-berlin.de/abar/aoet',
      author='Anton Bardishev',
      author_email='abar@protonmail.ch',
      license='MIT',
      packages=['aoet', 'aoet.analysis', 'aoet.parser', 'aoet.proxy', 'aoet.report'],
      install_requires=['numpy',
                        'matplotlib',
                        'sklearn',
                        'pandas'
                        ],
      scripts=['bin/aoet'],
      zip_safe=False)