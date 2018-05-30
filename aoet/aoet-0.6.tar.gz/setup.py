from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='aoet',
      version='0.6',
      description='Automation of Exploratory Testing',
      long_description=readme(),
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