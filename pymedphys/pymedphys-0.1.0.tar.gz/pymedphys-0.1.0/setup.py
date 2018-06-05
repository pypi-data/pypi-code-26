from setuptools import setup

setup(
    name="pymedphys",
    version="0.1.0",
    author="Simon Biggs",
    author_email="me@simonbiggs.net",
    description='Medical Physics python modules.',
    long_description=(
        'A range of python modules encompased under the pymedphys package, '
        'designed to be built upon for Medical Physics applications.'
    ),
    classifiers=[
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
    'Programming Language :: Python :: 3.6',
    'Topic :: Scientific/Engineering :: Medical Science Apps.',
    'Topic :: Scientific/Engineering :: Physics',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Healthcare Industry'
    ],
    packages=[
        "pymedphys"
    ],
    license='AGPLv3+',
    install_requires=[
        'numpy',
        'scipy',
        'pandas',
        'matplotlib',
        'attrs',
        'psutil',
        'pymssql',
        'keyring',
        'shapely',
        'pydicom',
    ]
)
