from setuptools import setup

requirements = [
    # package requirements go here
]

setup(
    name='HARK',
    version='0.8.0',
    description="Heterogenous Agents Resources & toolKit",
    author="Carroll, Christopher D; Palmer, Nathan; White, Matthew N.; Kazil, Jacqueline; Low, David C",
    author_email='ccarroll@llorracc.org',
    url='https://github.com/econ-ark/HARK',
    packages=['HARK'],
    entry_points={
        'console_scripts': [
            'HARK=HARK.cli:cli'
        ]
    },
    install_requires=requirements,
    keywords='HARK',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ]
)
