from setuptools import setup, find_packages


setup(name='x-mroy-1048',
    version='0.0.1',
    description=' x-mroy',
    url='https://github.com/Qingluan/.git',
    author='Qing luan',
    author_email='darkhackdevil@gmail.com',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    install_requires=['tornado==4.5.1','x-mroy-1046', 'mroylib-min'],
    entry_points={
        'console_scripts': ['x-local=LServer.lserver:run']
    },

)
