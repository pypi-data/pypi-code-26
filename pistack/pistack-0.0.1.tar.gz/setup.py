"""
setup.py for pistack
"""

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


setup(
    name='pistack',
    version='0.0.1',
    author='Philip Basford',
    author_email='p.j.basford@soton.ac.uk',
    license='Creative Commons Attribution-ShareAlike 4.0 International Public',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='pistack',
    platforms='any',
    packages=find_packages(exclude=['contrib', 'docs', 'test*']),
    install_requires=['pyserial'],
    python_requires='>=3.3, <4',
)
