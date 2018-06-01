from setuptools import setup, find_packages


setup(
    name='fidding-cli',
    version='2.0',
    description='A python cli project',
    url='https://github.com/fidding/python-cli.git',
    packages=find_packages(),
    author='fidding',
    author_email='395455856@qq.com',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    install_requires=[
        'Click',
    ],
    data_files=[('my_data', ['data/data.txt'])],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points='''
        [console_scripts]
        fidding-cli=python_cli.script.cli:cli
    ''',
)
