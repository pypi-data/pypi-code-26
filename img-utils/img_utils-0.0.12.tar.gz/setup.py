# from distutils.core import setup
from setuptools import setup

setup(
    name='img_utils',
    version='0.0.12',
    packages=['img_utils', 'img_utils.images', 'img_utils.files', 'img_utils.colors'],
    url='https://github.com/DewMaple/img_utils',
    description='Convenient functions that help to process images',
    author='dew.maple',
    author_email='dew.maple@gmail.com',
    license='MIT',
    keywords=['computer vision', 'image processing', 'opencv', 'numpy'],
    classifiers=['Programming Language :: Python :: 3.6'],
    project_urls={
        'Bug Reports': 'https://github.com/DewMaple/img_utils/issues',
        'Source': 'https://github.com/DewMaple/img_utils',
    },
    zip_safe=True
)
