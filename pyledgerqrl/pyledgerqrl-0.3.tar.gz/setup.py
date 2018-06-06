from setuptools import setup

setup(name='pyledgerqrl',
    version='0.3',
    description='python module for Ledger Nano S',
    url='https://github.com/theQRL/ledger-qrl',
    author='The QRL Team',
    author_email='info@theqrl.org',
    license='MIT',
    packages=['pyledgerqrl'],
    install_requires=['ledgerblue'],
    zip_safe=False)
