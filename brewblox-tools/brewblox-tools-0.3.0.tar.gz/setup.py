from setuptools import setup, find_packages


setup(
    name='brewblox-tools',
    use_scm_version={'local_scheme': lambda v: ''},
    url='https://github.com/BrewBlox/brewblox-service',
    author='BrewPi',
    author_email='development@brewpi.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='brewblox devops',
    packages=find_packages(exclude=['test']),
    install_requires=[
        'docker',
    ],
    python_requires='>=3.6',
    extras_require={'dev': ['tox']},
    setup_requires=['setuptools_scm'],
    entry_points={
        'console_scripts': [
            'bbt-distcopy = brewblox_tools.distcopy:main',
            'bbt-bump = brewblox_tools.bump:main',
            'bbt-deploy-docker = brewblox_tools.deploy_docker:main',
        ]
    }
)
