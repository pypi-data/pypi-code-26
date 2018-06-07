import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='intelecom',
    version='v0.0.2',
    author='Joseph G. Serunjogi',
    author_email='joseph.serunjogi@hotmail.com',
    description='Huawei IN interface library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/joeseggie/intelecom',
    packages=setuptools.find_packages(),
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ),
)
