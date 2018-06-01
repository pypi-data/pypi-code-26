import glob

from setuptools import setup

setup(
    name='rucio-clients-eiscat3d',
    version='0.0.2',
    data_files=[('etc/', glob.glob('etc/*.cfg'))],
    include_package_data=True,
    author="Rucio",
    description="Rucio Client Configuration for XDC",
    license="Apache License, Version 2.0",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX :: Linux',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Environment :: No Input/Output (Daemon)'],
    install_requires=['rucio-clients>=1.6.0'],
)
