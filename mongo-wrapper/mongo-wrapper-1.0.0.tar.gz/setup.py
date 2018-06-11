from setuptools import setup, find_packages

setup(
    name='mongo-wrapper',
    version='1.0.0',
    packages=find_packages(),
    install_requires=['pymongo>=3.0'],
    description='A thin wrapper around PyMongo. Used to simplify using MongoClient.',
    author='Wesley Uykimpang',
    author_email='wesu07@gmail.com',
    license='MIT',
    keywords='mongodb mongo nosql',
    url='https://github.com/wesuuu/mongo_adapter'
)
