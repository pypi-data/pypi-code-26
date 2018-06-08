from setuptools import setup, find_packages, Extension
from os.path import join, dirname

# extension = Extension('demo', sources=['demo.cpp'])

setup(
    name='ndicom_region_growing',
    version='0.0.1.dev0',
    author='Roman Baigildin',
    author_email='egdeveloper@mail.ru',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
    ],
    url='http://github.com/reactmed/neurdicom-plugins',
    license='MIT',
    keywords='DICOM',
    packages=find_packages(),
    install_requires=[
        'pydicom', 'dipy', 'numpy', 'opencv-python', 'scikit-learn'
    ],
    dependency_links=[
        "git+git://github.com/pydicom/pydicom"
    ],
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
    include_package_data=True,
    package_data={'': ['extension/build/Darwin/*.dylib']}
)
