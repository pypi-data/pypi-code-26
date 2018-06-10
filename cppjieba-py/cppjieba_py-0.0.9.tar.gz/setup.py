from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import setuptools
import os

from distutils.sysconfig import get_python_lib
site_package_dir = get_python_lib() + os.path.sep

__version__ = '0.0.9'

class get_pybind_include(object):
    """Helper class to determine the pybind11 include path
    The purpose of this class is to postpone importing pybind11
    until it is actually installed, so that the ``get_include()``
    method can be invoked. """

    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)

ext_modules = [
    Extension(
        'libcppjieba',
        ['src/main.cpp'],
        include_dirs=[
            # Path to pybind11 headers
            get_pybind_include(),
            get_pybind_include(user=True),
            "cppjieba/include",
            "cppjieba/deps"
        ],
        language='c++'
    ),
]


# As of Python 3.6, CCompiler has a `has_flag` method.
# cf http://bugs.python.org/issue26689
def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.cpp') as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        try:
            compiler.compile([f.name], extra_postargs=[flagname])
        except setuptools.distutils.errors.CompileError:
            return False
    return True


def cpp_flag(compiler):
    """Return the -std=c++[11/14] compiler flag.
    The c++14 is prefered over c++11 (when it is available).
    """
    if has_flag(compiler, '-std=c++14'):
        return '-std=c++14'
    elif has_flag(compiler, '-std=c++11'):
        return '-std=c++11'
    else:
        raise RuntimeError('Unsupported compiler -- at least C++11 support '
                           'is needed!')


class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""
    c_opts = {
        'msvc': ['/EHsc'],
        'unix': [],
    }

    if sys.platform == 'darwin':
        c_opts['unix'] += ['-stdlib=libc++', '-mmacosx-version-min=10.7']

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        if ct == 'unix':
            opts.append('-DVERSION_INFO="%s"' %
                        self.distribution.get_version())
            opts.append('-DSITE_PACKAGE_PATH="%s"' %
                        site_package_dir)
            opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, '-fvisibility=hidden'):
                opts.append('-fvisibility=hidden')
        elif ct == 'msvc':
            opts.append('/DVERSION_INFO=\\"%s\\"' %
                        self.distribution.get_version())
            opts.append('/DSITE_PACKAGE_PATH=\\"%s\\"' %
                        site_package_dir)
        for ext in self.extensions:
            ext.extra_compile_args = opts
        build_ext.build_extensions(self)

install_requires = ['pybind11>=2.2']

extras_require = {
        'test': ['spec==1.4.1']
    }

if sys.version_info[0] <3:
    extras_require["test"].append("pathlib2")

classifiers = [
    'License :: OSI Approved :: MIT License',
    'Natural Language :: Chinese (Simplified)',
    'Natural Language :: Chinese (Traditional)',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: C++',
    'Operating System :: Unix',
    'Topic :: Text Processing :: Linguistic',
    'Topic :: Software Development :: Libraries :: Python Modules'
]

setup(
    name='cppjieba_py',
    version=__version__,
    author='bung87,yeping zheng',
    url='https://github.com/bung87/cppjieba-py/',
    description='python bindings of cppjieba',
    long_description= open("README.md").read(),
    classifiers = classifiers,
    ext_modules=ext_modules,
    packages=['cppjieba_py','cppjieba.dict'],
    package_data = {
        'cppjieba.dict': ['*.utf8']
     },
    include_package_data=True,
    install_requires=install_requires,
    extras_require=extras_require,
    cmdclass={'build_ext': BuildExt},
    zip_safe=False,
)
