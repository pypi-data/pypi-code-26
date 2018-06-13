import re
from setuptools import setup, find_packages

# read the version number from source
version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('screenshotapi/screenshotapi.py').read(),
    re.M
    ).group(1)

try:
    # in addition to pip install pypandoc, might have to: apt install -y pandoc
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError) as e:
    print("Error converting READMD.md to rst:", str(e))
    long_description = open('README.md').read()

setup(name='screenshotapi',
      version=version,
      description='Python API Client for Screenshotapi.io',
      long_description=long_description,
      keywords=['screenshot'],
      author='Doug Kerwin',
      author_email='dwkerwin@gmail.com',
      url='https://github.com/screenshotapi/screenshotapi-python',
      packages=find_packages(),
      install_requires=[
        'requests>=2.18.4, <3.0',
        'six>=1.11.0, <2.0'
      ],
      entry_points={
        "console_scripts": ['screenshotapi = screenshotapi.screenshotapi:main']
      },
      license='MIT',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        ]
     )
