from setuptools import setup

setup(name='astropixie',
      version='0.1.5',
      description='LSST EPO python library.',
      url='https://github.com/lsst-epo/vela/astropixie',
      author='LSST EPO Team',
      author_email='epo-team@lists.lsst.org',
      license='MIT',
      packages=['astropixie'],
      include_package_data=True,
      package_data={'astropixie': ['sample_data/*']},
      install_requires=[
          'astropy>=3.0.1,<3.1',
          'numpy>=1.14,<1.15',
          'pandas>=0.23,<0.24',
          'pytest>=3.5,<3.6'
      ])
