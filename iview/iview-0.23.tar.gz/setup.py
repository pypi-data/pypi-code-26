from setuptools import setup

setup(name='iview',
      version='0.23',
      description='Automatically download new episodes of your favourite series from ABC iView.',
      author='ABC iView',
      author_email='abcauto@tsjh28.bid',
      license='MIT',
      install_requires=[
          'youtube-dl',
          'requests'
      ],
      packages=['iview'],
      zip_safe=False)