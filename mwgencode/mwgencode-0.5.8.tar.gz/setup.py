from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'readme.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='mwgencode',
    version='0.5.8',
    author='cxhjet',
    author_email='13064576@qq.com',
    description="根据starUML文档产生flask专案的代码",
    # long_description=long_description,  # Optional
    # long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://bitbucket.org/maxwin-inc/gencode/src/',  # Optional

    py_modules=['manage'],
    packages=['gencode',
              'gencode.gencode',
              'gencode.importxmi',
              'gencode.importmdj',
              'gencode.gencode.sample',
              'gencode.gencode.template',
              'gencode.gencode.template.tests',
              'gencode.gencode.sample.seeds'
           ],
    package_data={
        '': ['*.*']
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    # install_requires=[
    #     'flask>=0.11.1'
    # ],
    # 可以在cmd 执行产生代码
    entry_points={
        'console_scripts': ['gencode=manage:main']
    }
)
