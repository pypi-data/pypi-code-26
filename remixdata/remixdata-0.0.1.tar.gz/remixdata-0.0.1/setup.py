from setuptools import setup

setup(
    name = 'remixdata',
    version = '0.0.1',
    url = 'https://github.com/remix/data-tools',
    author = 'Michal Migurski',
    author_email = 'mike@remix.com',
    description = 'Tools, requirements, utilities for Remix data use.',
    packages = ['remixdata'],
    install_requires = [
        'jupyter == 1.0.0',
        'pandas == 0.23.0',
        ]
)
