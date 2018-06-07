import setuptools

setuptools.setup(
    name='FixedWidth',
    packages=['fixedwidth'],
    version='1.2',
    description='Two-way fixed-width <--> Python dict converter.',
    author='Shawn Milochik',
    author_email='shawn@milochik.com',
    url='https://github.com/ShawnMilo/fixedwidth',
    install_requires=['six'],
    license='BSD',
    keywords='fixed width',
    test_suite="fixedwidth.tests",
    classifiers=[],
)
