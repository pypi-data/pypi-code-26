#-- powertools.setup.arguments

'''
another standard library extension
'''

from copy import deepcopy
#----------------------------------------------------------------------------------------------#

kwargs = dict(
    name        = 'powertools',
    packages    = ['powertools', 'powertools.setup'],
    version     = '0.0.6',
    description = __doc__,
    license     = "MIT License",

    url         ='https://github.com/philipov/powertools',
    author      ='Philip Loguinov',
    author_email='philipov@gmail.com',

    zip_safe                = True,
    include_package_data    = True,

    install_requires=[
        'pytest',
        'colored_traceback',
        'colorama',
        'coloredlogs',
        'termcolor',
        'ordered_set'
    ],
    classifiers=[
        'Environment :: Console',
        'Environment :: Other Environment',

        'Intended Audience :: Information Technology',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Customer Service',

        'License :: Other/Proprietary License',

        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: POSIX :: Linux',

        'Programming Language :: Python :: 3.6'
    ]
)

test_kwargs = deepcopy( kwargs )
dev_kwargs  = deepcopy( test_kwargs )

__version__ = kwargs['version']


#----------------------------------------------------------------------------------------------#
