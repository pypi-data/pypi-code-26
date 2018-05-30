# coding: utf-8

from setuptools import find_packages, setup

setup(
    name='paas-star',
    version='0.1.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=["toolkity", "star-builder", "boto", "motor"],
    author='shichao.ma',
    author_email='shichao.ma@yiducloud.cn',
    description='''package description here''',
    entry_points={
        'console_scripts': [
            'paas-create = paas_star:main',
        ],
    },
    keywords='',
    
)