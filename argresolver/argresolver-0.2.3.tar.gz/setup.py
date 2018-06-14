from setuptools import setup, find_packages


VERSION = '0.2.3'


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='argresolver',
    version=VERSION,
    description="Resolve missing arguments at runtime",
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/HazardDede/argresolver',
    author='d.muth',
    author_email='d.muth@gmx.net',
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='args arguments injection resolve resolver',
    project_urls={
        'Documentation': 'https://github.com/HazardDede/argresolver/blob/master/README.md',
        'Source': 'https://github.com/HazardDede/argresolver/',
        'Tracker': 'https://github.com/HazardDede/argresolver/issues',
    },
    packages=find_packages(exclude=[]),
    install_requires=[
    ],
    python_requires='>=3.4',
    include_package_data=True
)
