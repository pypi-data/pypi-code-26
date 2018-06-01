from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(name='cleverbotio',
    version="1.0",
    description="A Python wrapper for the Cleverbot.io API that has an async option",
    long_description=readme,
    url='https://github.com/shadeyg56/cleverbotio.py',
    author='shadeyg56',
    license="GNU",
    packages=['Cleverbotio', 'Cleverbotio.async'],
    install_requires=['requests>=1.0.0'],
    extras_require={'async': ['aiohttp>=1.0.0']},
    keywords = ["cleverbot", "async", "api-wrapper"]
)