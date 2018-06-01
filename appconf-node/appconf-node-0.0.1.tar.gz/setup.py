import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="appconf-node",
    url="https://github.com/novopl/appconf-node",
    version=read('VERSION').strip(),
    author="Mateusz 'novo' Klos",
    author_email="novopl@gmail.com",
    license="MIT",
    description="Manage a single bare-metal node",
    long_description=read('README.rst'),
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        l.strip() for l in read('requirements.txt').split() if '==' in l
    ],
    package_data={
        'appconf_node': ['run/config.json', 'static/*']
    },
    entry_points={
        'console_scripts': [
            'appconf-node = appconf_node.cli:cli',
        ]
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
    ],
)
