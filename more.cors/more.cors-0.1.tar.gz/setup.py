import io
from setuptools import setup, find_packages

long_description = (
    io.open('README.rst', encoding='utf-8').read()
    + '\n\n' +
    io.open('CHANGES.rst', encoding='utf-8').read())

version = '0.1'

setup(name='more.cors',
      version=version,
      description="CORS support for Morepath",
      long_description=long_description,
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      keywords='morepath CORS',
      author='Izhar Firdaus',
      author_email='kagesenshi.87@gmail.com',
      url='http://github.com/kagesenshi/more.cors',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      namespace_packages=['more'],
      zip_safe=False,
      install_requires=[
          'setuptools',
          'morepath',
      ],
      entry_points={
          'morepath': [
              'scan = more.cors'
          ]
      },
      extras_require=dict(
          test=[
              'pytest',
              'pytest-remove-stale-bytecode',
              'webtest'
          ],
          coverage=[
              'pytest-cov',
          ],
          pep8=[
              'flake8',
              'pep8-naming',
          ],
      ))
