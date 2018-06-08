from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path
from setuptools.command.install import install
import re
import ast

_version_re = re.compile(r'__version__\s+=\s+(.*)')
version = str(ast.literal_eval(
    _version_re.search(
        open('dome/__init__.py').read()
    ).group(1)
))
here = path.abspath(path.dirname(__file__))


class MyInstall(install):
    def run(self):
        print("-- installing... --")
        install.run(self)

setup(
        name = 'dome',
        version=version,
        description='Python DOM Element template',
        long_description='\nREADME: https://github.com/qorzj/dome\n',
        url='https://github.com/qorzj/dome',
        author='qorzj',
        author_email='inull@qq.com',
        license='MIT',
        platforms=['any'],

        classifiers=[
            ],
        keywords='dome dom lessweb',
        packages = ['dome'],
        install_requires=[],

        cmdclass={'install': MyInstall},
        entry_points={
            'console_scripts': [
                ],
            },
    )
