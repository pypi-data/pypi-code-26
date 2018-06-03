from setuptools import setup

with open('README.rst') as readme:
    readme = readme.read()

setup(
    name='dev_identify',
    packages=['dev_identify'],
    version='0.0.1',
    description='A simple python wrapper for dev-identify image grabber.',
    long_description=readme,
    author='Rahul Haque',
    author_email='rahulhaque07@gmail.com',
    install_requires=[
        'requests',
    ],
    license='MIT',
    url='https://github.com/rahulhaque/dev-identify-python',
    download_url='https://github.com/rahulhaque/dev-identify-python/archive/v0.0.1.tar.gz',
    keywords=['python', 'dev-identify', 'api-wrapper'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)
