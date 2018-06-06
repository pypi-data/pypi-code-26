from setuptools import setup, find_packages

setup(
    name='rucio_arc',
    version='0.0.5',
    author="Rucio",
    description="rucio-arc is an extension for Rucio, e.g., ARC data delivery service",
    license="Apache License, Version 2.0",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX :: Linux',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Environment :: No Input/Output (Daemon)'],
    install_requires=['M2Crypto', 'cryptography>=2.2.2'],
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    entry_points={
        'console_scripts': ['rucio-arc=rucio_arc.arc:main'],
        'rucio_transfertools': ['ARC=rucio_arc.arc:ARC'],
        },
)
