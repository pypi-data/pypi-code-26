from setuptools import setup

setup(name='astropixie-widgets',
      version='0.1.7.1',
      description='LSST EPO ',
      url='https://github.com/lsst-epo/vela/astropixie-widgets',
      author='LSST EPO Team',
      author_email='epo-team@lists.lsst.org',
      license='MIT',
      packages=['astropixie_widgets'],
      include_package_data=True,
      package_data={'astropixie': ['sample_data/*']},
      install_requires=[
          'astropixie==0.1.7',
          'astropy>=3.0.1,<3.1',
          'astroquery>=0.3.8',
          'bokeh>=0.12.16',
          # 'ipyaladin',
          'numpy>=1.14.2,<1.16',
          'pandas',
          'pytest',
          'scipy'
      ])
