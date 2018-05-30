from setuptools import setup


setup(
    name='ParticleFlow',
    version='0.0.1',
    description='Particle simulations with tensorflow',
    long_description='',
    long_description_content_type='text/x-rst',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Physics',
    ],
    keywords=['simulation', 'framework'],
    url='https://gitlab.com/IPMsim/ParticleFlow',
    author='Dominik Vilsmeier',
    author_email='dominik.vilsmeier1123@gmail.com',
    license='GPL-3.0',
    packages=[],
    install_requires=[
        'hanna',
        'injector',
        'rx',
        'scipy',
        'tensorflow'
    ],
    python_requires='>=3.6',
    include_package_data=True,
    zip_safe=False
)
