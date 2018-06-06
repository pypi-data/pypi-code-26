import os
import sys
import shutil
from setuptools import setup, find_packages
from distutils.sysconfig import get_python_lib
from subprocess import call
from setuptools.command.install import install
from distutils.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext


#  os.environ['CC'] = 'g++'
#  os.environ['CXX'] = 'g++'

major = str(sys.version_info.major)
minor = str(sys.version_info.minor)

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
VERSION = 'python' + major + '.' + minor
LIB_PATH = get_python_lib()
print(ROOT_PATH)


class CustomBuild(install):
    def run(self):
        call(['bash', 'install_depends.sh'])
        install.run(self)


class MyBuildExt(build_ext):
    def run(self):
        build_ext.run(self)
        build_dir = os.path.realpath(self.build_lib)
        root_dir = os.path.dirname(os.path.realpath(__file__))
        target_dir = build_dir if not self.inplace else root_dir
        if not os.path.exists(target_dir + '/hatshufflepy'):
            os.makedirs(target_dir + '/hatshufflepy')
        self.copy_file('hatshufflepy/libhatshuffle/lib/libhatshuffle.so',
                       root_dir, target_dir + '/hatshufflepy/libhatshuffle.so')
        self.copy_file('hatshufflepy/libhatshuffle/lib/libff.so',
                       root_dir, target_dir + '/hatshufflepy/libff.so')
        self.copy_file('hatshufflepy/libhatshuffle/lib/libzm.so',
                       root_dir, target_dir + '/hatshufflepy/libzm.so')

    def copy_file(self, path, source_dir, destination_dir):
        if os.path.exists(os.path.join(source_dir, path)):
            shutil.copyfile(os.path.join(source_dir, path),
                            destination_dir)


module = Extension('hatshufflepy',
                   sources=['hatshufflepy/hatshufflepy.pyx'],
                   language='c++',
                   include_dirs=['hatshufflepy/libhatshuffle/include/libhatshuffle',
                                 'hatshufflepy/libhatshuffle/include',
                                 'libhatshuffle/include/libff'],
                   libraries=['zm', 'ff', 'hatshuffle'],
                   library_dirs=['/usr/local/lib',
                                 'hatshufflepy/libhatshuffle/lib'],
                   runtime_library_dirs=[ROOT_PATH +
                                         '/hatshufflepy/libhatshuffle/lib',
					 '/usr/local/lib/' + VERSION + #  ubuntu
					 '/dist-packages/hatshufflepy',
					 LIB_PATH + '/hatshufflepy'],
                   extra_compile_args=['-std=c++11', '-fPIC',
                                       '-shared', '-w',
                                       '-static', '-O3'],
                   extra_link_args=['-lgmp', '-fopenmp', '-g'])


setup(
    name='hatshufflepy',
    version='0.0.5',
    packages=find_packages(),
    author='Stefanos Chaliasos',
    author_email='stefanoshaliassos@gmail.com',
    description='Cython wrapper for hat shuffle implementation',
    license='MIT',
    keywords='mixnet ecc',
    url='https://github.com/StefanosChaliasos/hatshufflepy',

    install_requires=["cython >= 0.22.1"],
    ext_modules=cythonize(module),
    cmdclass={'build_ext': MyBuildExt, 'install': CustomBuild},
)
