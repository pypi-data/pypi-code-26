from numpy.distutils.core import Extension

fortran_src = ['simulate', 'fit']
fortran_ext = [
    Extension(
        name='f90_' + f,
        sources=['./fem/f90_' + f + '.f90', './fem/f90_' + f + '.pyf'])
    for f in fortran_src
]

with open('README.rst', 'r') as f:
    readme = f.read()

with open('version', 'r') as f:
    version = f.read()

if __name__ == '__main__':
    from numpy.distutils.core import setup

    setup(
        name='fem',
        version=version,
        description='Free Energy Minimization',
        long_description=readme,
        author='Joseph P. McKenna',
        author_email='joepatmckenna@gmail.com',
        url='http://lbm.niddk.nih.gov/mckennajp/fem',
        download_url='https://pypi.org/project/fem',
        packages=['fem'],
        ext_modules=fortran_ext,
        classifiers=("Programming Language :: Python :: 2",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent"),
        license='MIT',
        keywords=['inference', 'statistics', 'machine learning'],
        data_files=[])
