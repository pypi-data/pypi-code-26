from setuptools import setup, find_packages

setup(name='travdeploy',
      version='0.0.5',
      description=u"Skeleton of a Python package",
      classifiers=[],
      keywords='',
      author=u"Jacques Tardie",
      author_email='hi@jacquestardie.org',
      url='https://github.com/jacquestardie/travdeploy',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'click'
      ],
      extras_require={
          'test': ['pytest', 'pytest-cov', 'codecov'],
      },
      entry_points="""
      [console_scripts]
      travdeploy=travdeploy.scripts.cli:cli
      """
      )
