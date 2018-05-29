from setuptools import setup, find_packages

print(find_packages())
setup(
    name='b26_toolkit',
    version='0.1a1',
    packages=['b26_toolkit', 'b26_toolkit.core', 'b26_toolkit.data_analysis', 'b26_toolkit.data_processing',
              'b26_toolkit.gui', 'b26_toolkit.plotting', 'b26_toolkit.scripts', 'b26_toolkit.instruments'],
    url='https://github.com/LISE-B26/b26_toolkit',
    license='GPL',
    author='Arthur Safira, Jan Gieseler, and Aaron Kabcenell',
    author_email='asafira@fas.harvard.edu',
    description='Python Laboratory Control Software',
    keywords='laboratory experiment control',
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Development Status :: 4 - Beta',
        'Environment :: Win32 (MS Windows)',
        ],
    install_requires=[
        'matplotlib',
        'pandas',
        'numpy',
        'scipy',
        'pyyaml',
        'PyQt5',
        'PyVISA',
        'trackpy',
        'scikit_image',
        'ipywidgets',
        'PIMS',
        'Pillow',
        'peakutils',
        'pyserial',
        'pylabcontrol'
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
)
