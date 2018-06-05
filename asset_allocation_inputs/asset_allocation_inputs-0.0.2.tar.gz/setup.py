from setuptools import setup

exec (open('asset_allocation_inputs/version.py').read())

setup(
    name='asset_allocation_inputs',
    version=__version__,
    author='viv-r',
    packages=['asset_allocation_inputs'],
    include_package_data=True,
    license='MIT',
    description='Dash UI component suite',
    install_requires=[]
)
