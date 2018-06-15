from setuptools import setup, find_packages

packages = find_packages()
classifiers = ['Development Status :: 5 - Production/Stable', 'Intended Audience :: Developers',
               'License :: OSI Approved :: MIT License', 'Natural Language :: English', 'Operating System :: '
                                                                                        'Microsoft :: Windows',
               'Operating System :: Unix', 'Programming Language :: Python', 'Programming Language :: Python :: 3',
               'Programming Language :: Python :: 3.6', 'Topic :: Software Development :: Libraries :: Python Modules',
               'Topic :: Software Development :: Testing', 'Topic :: Utilities']
requirements = ['colorlog']
version = '1.0'
setup(name='colorlogger', version=version, url='https://github.com/PokeTec/colorlogger', author='PokestarFan',
      author_email='pokestarfan@yahoo.com', maintainer='PokestarFan', maintainer_email='pokestarfan@yahoo.com',
      description='Easily log in color', platforms='Windows, Mac, Linux', license='MIT License', packages=packages,
      install_requires=requirements, classifiers=classifiers)
