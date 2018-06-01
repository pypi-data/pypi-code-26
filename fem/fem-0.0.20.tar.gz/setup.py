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


def increment_version_number():
    with open('version', 'r') as f:
        version = f.read()
    version = [int(v) for v in version.split('.')]
    base = [10, 10, 100]
    i = 2
    version[i] += 1
    while version[i] == base[i]:
        i -= 1
        version[i] += 1
    for j in range(i + 1, 3):
        version[j] = 0
    version = [str(v) for v in version]
    version = '.'.join(version)
    with open('version', 'w') as f:
        f.write(version)
    return version


if __name__ == '__main__':
    from numpy.distutils.core import setup

    setup(
        name='fem',
        version=increment_version_number(),
        packages=['fem'],
        ext_modules=fortran_ext,
        author='Joseph P. McKenna',
        author_email='joepatmckenna@gmail.com',
        description='Free Energy Minimization',
        long_description=readme,
        url='http://lbm.niddk.nih.gov/mckennajp/fem',
        classifiers=("Programming Language :: Python :: 2",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent"))
