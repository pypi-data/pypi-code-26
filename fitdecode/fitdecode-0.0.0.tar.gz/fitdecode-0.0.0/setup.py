import os.path
import setuptools

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), mode='r', encoding='utf-8') as f:
    readme = f.read()

setuptools.setup(
    name='fitdecode',
    version='0.0.0',
    description='[WiP; Name Squatting] - FIT files parser and decoder',
    long_description=readme,
    author='Jean-Charles Lefebvre',
    author_email='polyvertex@gmail.com',
    url='https://github.com/polyvertex/fitdecode',
    license='MIT',
    keywords=['fit', 'ant', 'file', 'parse', 'parser', 'decode', 'decoder'],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6'],

    packages=[],

    python_requires='>=3.6',
    install_requires=[],
    extras_require={})
