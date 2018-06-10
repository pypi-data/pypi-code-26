import re
from setuptools import setup

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('finfunctions/__init__.py').read(),
    re.M
    ).group(1)

with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")

setup(name='fin-functions',
      description='fin-functions',
      entry_points = {
        'console_scripts': ['fin-functions=finfunctions.main:main']
        },
      url='https://github.com/njfix6/fin-functions',
      author='Nicholas Fix',
      author_email='njfix6@gmail.com',
      packages=['finfunctions'],
      long_description = long_descr,
      version=version
)
