from setuptools import setup, find_packages

setup(
    name='totonesmovies',
    author='Daniel Flor',
    author_email='danielhernanflor@gmail.com',
    version='0.4dev',
    packages=['totonesmovies'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README').read(),
    url='https://github.com/danielhf/totonesmovies',
    dependencies_links=['https://github.com/alberanid/imdbpy'],
    install_requires=['pyquery','requests','pprint']
)