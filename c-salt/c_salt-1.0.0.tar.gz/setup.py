from setuptools import setup, find_packages

setup(
    name='c_salt',
    version='1.0.0',
    description='Sales and Leads prediction for Franchise dealers',
    url='https://git.corp.tc/lgolod/C_SALT/tree/master/packages/c_salt',
    author='Lev Golod',
    author_email="lgolod@truecar.com",
    license='Proprietary',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['sklearn',
    'scipy',
    ],
    zip_safe=False,
#     entry_points={"console_scripts": ["grundo = grundo.__main__:main"]},
)