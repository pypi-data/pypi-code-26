from setuptools import setup
from os import path

current_path = path.abspath(path.dirname(__file__))
with open(path.join(current_path, 'README.rst'), encoding='utf-8') as file:
      long_description = file.read()

setup(name='licenseit',
      version='0.1.0',
      description='CLI for generationg a license files.',
      long_description=long_description,
      url='https://github.com/monzita/licenseit',
      author='Monika Ilieva',
      author_email='hidden@hidden.com',
      license='MIT',
      keywords='cli license generator',
      packages=['licenseit'],
      package_dir={'licenseit' : 'licenseit'},
      package_data={'licenseit': ['*.txt', 'licenses/content/*']},
      py_modules=['licenseit.commands', 'licenseit.commands.new', 'licenseit.licenses', 'licenseit.licenses.license'],
      install_requires = ['docopt'],
      entry_points = {
      	'console_scripts': [
      		'licenseit=licenseit.cli:main'
      	],
      },
      classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3 :: Only',
            'Topic :: Utilities'
      ],
      zip_safe=True)