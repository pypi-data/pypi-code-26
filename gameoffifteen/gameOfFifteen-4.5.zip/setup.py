from setuptools import setup

def readme():
    with open('readme.rst') as f:
        return f.read()

setup(name='gameOfFifteen',
      version='4.5',
      description='The game of fifteen',
      long_description=readme(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Games/Entertainment :: Puzzle Games',
      ],
      keywords='Sliding puzzle',
      url='https://github.com/gameOfFifteen',
      author='Dev: Vikarowitsch Test: Softy',
      author_email='vikarowitsch@yahoo.de',
      license='MIT',
      packages=['gameOfFifteen'],
      install_requires=[
          'Pillow',
      ],
      include_package_data=True,
      zip_safe=False)

