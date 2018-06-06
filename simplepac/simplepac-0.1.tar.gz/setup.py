import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='simplepac',
    version='0.1',
    description='Generate a simple pac for proxy and ad-block',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Taosky/simplepac',
    author='Taosky',
    author_email='t@firefoxcn.net',
    license='GPL-3.0',
    packages=['simplepac'],
    package_data={
        'simplepac': ['resources/*']
    },
    entry_points={
        'console_scripts': ['simplepac=simplepac.core:run'],
    },
    install_requires=[
        'requests==2.18.4',
        'matplotlib==2.2.2',
        'numpy==1.14.3',
        'sklearn',
        'scipy==1.1.0',
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ),
    zip_safe=False)
