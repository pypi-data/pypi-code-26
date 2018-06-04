from setuptools import setup

setup(name='genespider4python',
      version='0.1.01',
      description='The python translation of the MATLAB genespider package.',
      url='https://gitlab.com/Xparx/genespider4python',
      author='Andreas Tjärnberg',
      author_email='andreas.tjarnberg@fripost.org',
      license='LGPL',
      packages=['gspy', 'gsexamples'],
      python_requires='>=3',
      install_requires=[
          'numpy',
          'pandas',
          'sklearn',
          'scipy',
          'fisher',
      ],
      zip_safe=False)
