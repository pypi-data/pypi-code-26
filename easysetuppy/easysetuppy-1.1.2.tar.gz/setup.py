from setuptools import setup, find_packages

packages = find_packages()
classifiers = ['Development Status :: 5 - Production/Stable', 'Intended Audience :: Developers',
               'License :: OSI Approved :: MIT License', 'Natural Language :: English',
               'Operating System :: Microsoft :: Windows', 'Operating System :: Unix', 'Programming Language :: Python',
               'Programming Language :: Python :: 3', 'Programming Language :: Python :: 3.6',
               'Topic :: Software Development', 'Topic :: Utilities']
version = '1.1.2'
requirements = ['easygui', 'wheel', 'twine', 'setuptools']
gui_scripts = ['easysetuppy = easysetuppy:main',
               'EasySetupPy = easysetuppy:main',
               'build = easysetuppy:build_and_upload',
               ]
setup(name='easysetuppy', version=version, url='https://www.github.com/PokeTec/EasySetup', author='PokestarFan',
      author_email='pokestarfan@yahoo.com', maintainer='PokestarFan', maintainer_email='pokestarfan@yahoo.com',
      description='A program to make easy setup.py files', platforms='Windows, Mac, Linux', license='MIT License',
      packages=packages, requirements=requirements, classifiers=classifiers, entry_points={'gui_scripts': gui_scripts}
      )
