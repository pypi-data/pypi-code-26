import setuptools

import paraproc

with open('README.rst', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='paraproc',
    version=paraproc.__version__,
    author='herrlich10',
    author_email='herrlich10@gmail.com',
    description='Easy parallel processing in Python',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/herrlich10/paraproc',
    py_modules=['paraproc'],
    install_requires=[
        # 'numpy',
    ],
    classifiers=(
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ),
)