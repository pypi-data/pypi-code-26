from setuptools import setup, find_packages
import os

with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(name='dhpcclient',
    version='0.5.5',
    author='jonathan ehrengruber',
    author_email='jonathan.ehrengruber@students.fhnw.ch',
    description='Distributed High Performance Cluster Client for a heterogen Operating System environment',
    keywords='dhpc hpc high performance cluster client',
    url='https://gitlab.fhnw.ch',
    packages=['dhpcclient'],
    data_files=[('/dhpcclient/share/', ['dhpcclient/share/config_linux.ini']),  # Default configs
        ('/dhpcclient/share/', ['dhpcclient/share/config_windows.ini']),
        ('/dhpcclient/res/', ['dhpcclient/res/icon.png']),
        ('/dhpcclient/etc/', ['dhpcclient/etc/empty.txt'])  # Empty dir for config
    ],
    setup_requires=['pytest-runner'],
    install_requires=required,
    tests_require=['pytest', 'pytest-mock'],
    entry_points = {
        'console_scripts': ['hpcclient-gui=dhpcclient.gui:main', 'hpcclient-svc=dhpcclient.hpcclient:main']
    },
    extras_require={
        ':sys_platform == "win32"': ['wxpython>=4.0.1'],
    }
)
