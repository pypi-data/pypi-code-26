from setuptools import setup, find_packages

LONG_DESCRIPTION = """
+ Clean pandas DataFrame to tidy DataFrame
+ Inspired by tidyr in R
+ Goal: Help you to create **tidy Pandas Dataframe**
+ Wapper window function from DataFrame
+ Implement R function *tidyr::gather* and *tidyr:spread* using python

"""

setup(
    name='tidyframe',
    version='0.0.1',
    author='Hsueh-Hung Cheng',
    author_email='jhengsh.email@gmail.com',
    url='https://github.com/Jhengsh/tidyframe',
    description='Clean pandas DataFrame to Tidy DataFrame',
    long_description=LONG_DESCRIPTION,
    keywords=['pandas', 'tidy'],
    packages=find_packages(),
    license='MIT',
    platforms='any',
    python_requires='!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
    install_requires=["pandas"],
)
