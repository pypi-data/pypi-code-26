from setuptools import setup

setup(
    name='mongoladdu',
    version='0.0.1',
    url='https://github.com/dataladdu/mongoladdu',
    download_url='https://github.com/dataladdu/mongoladdu/archive/0.0.1.tar.gz',
    license='MIT',
    author='Deepan Subramani',
    author_email='subramani.deepan@gmail.com',
    description='MongoDB migration manager',
    long_description='Light weight migration manager for MongoDB using pymongo',
    keywords = ['mongodb', 'migration'],
    packages=['mongoladdu'],
    include_package_data=True,
    platforms='any',
    python_requires='>=3.4',
    install_requires=[
        'pymongo>=3.6.1',
        'click>=6.7',
        'PyYAML>=3.12'
    ],
    entry_points='''
        [console_scripts]
        mongoladdu=mongoladdu.cli:cli
    ''',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)