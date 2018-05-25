#!python3
from setuptools import setup

setup(
   name='lukis',
   version='0.18.5',
   description='Generate a device independent vector graphic stream that can be converted to pdf, svg, or other vector graphic format.',
   author='CHEN, Lee Chuin',
   author_email='leechuin@gmail.com',
   license='MIT',
   python_requires='>=3',
   long_description=open('README.rst').read(),
   classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Topic :: Scientific/Engineering :: Visualization',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
   keywords='lukis vector graphic pdf svg',
   packages=['lukis'],  #same as name
   install_requires=['numpy','pillow'], #external packages as dependencies
)
