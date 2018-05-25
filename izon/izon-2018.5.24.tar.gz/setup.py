from setuptools import setup, find_packages

requires = []

setup(
    name='izon',
    version='2018.5.24',
    description='A dependency handling tool for files',
    url='https://github.com/kmu/izon',
    author='Koki Muraoka',
    author_email='muraok_k@chemsys.t.u-tokyo.ac.jp',
    license='MIT',
    keywords='dependency time',
    packages=find_packages(),
    install_requires=requires,
    classifiers=[
        'Topic :: System :: Filesystems',
    ],
)
