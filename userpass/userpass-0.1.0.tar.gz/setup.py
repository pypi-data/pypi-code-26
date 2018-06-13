from io import open

from setuptools import find_packages, setup

with open('userpass/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.0.1'

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

REQUIRES = []

setup(
    name='userpass',
    version=version,
    description='Store username and password at $HOME',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Yongwen Zhuang',
    author_email='zyeoman@163.com',
    maintainer='Yongwen Zhuang',
    maintainer_email='zyeoman@163.com',
    url='https://github.com/zYeoman/userpass',
    license='MIT',

    keywords=[
        'password',
        'store',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    install_requires=REQUIRES,
    tests_require=['coverage', 'pytest'],

    packages=find_packages(),
)
