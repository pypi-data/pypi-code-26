from pathlib import Path

from importlib.machinery import SourceFileLoader

from setuptools import setup, find_packages


ver_module_path = Path(__file__).parent / Path('bnmutils/__version__.py')
ver_module_obj = SourceFileLoader('bnmutils', str(ver_module_path)).load_module()

version = ver_module_obj.__version__


requires = [
]

with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='bnmutils',
    packages=find_packages(exclude=['tests*']),
    install_requires=requires,
    version=version,
    description='Compilations of various utilities',
    long_description=readme,
    author='Luna Chen',
    url='https://github.com/BNMetrics/bnmetrics-utils',
    author_email='luna@bnmetrics.com',
    keywords=['configparser', '.ini', 'docstring'],
    python_requires='>=3',
    license='Apache 2.0',
)
