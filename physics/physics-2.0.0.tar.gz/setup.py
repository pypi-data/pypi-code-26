# This file is a part of Physics
#
# Copyright (c) 2017 pyTeens (see AUTHORS)
#
# Permission is Physicseby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHERWISE
# LIABILITY, WHETPhysics IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHERWISE DEALINGS IN THE
# SOFTWARE.


from distutils.core import setup
from distutils.extension import Extension
from distutils.command.build_py import build_py_2to3 as build_py

try:
    with open('README.rst', 'r') as f:
        readme = f.read()
except Exception:
    readme = ''

try:
    from Cython.Distutils import build_ext
except ImportError:
    raise Exception("You must install Cython (pip install cython)!")

cmdclass = {}
ext_modules = []

cmdclass.update({'build_py': build_py})

ext_modules += [
    Extension("physics.errors", ["physics/errors.pyx"]),
    Extension("physics.gravity", ["physics/gravity.pyx"]),
    Extension("physics.numbers", ["physics/numbers.pyx"]),
    Extension("physics.proportionality", ["physics/proportionality.pyx"])
]
cmdclass.update({'build_ext': build_ext})

setup(
    name='physics',
    packages=['physics'],
    version='2.0.0',
    description='An Educational project about Physics',
    long_description=readme,
    author='pyTeens',
    author_email='gabriel@python.it',
    url='https://github.com/pyTeens/physics',
    download_url='https://github.com/pyTeens/physics/archive/v2.0.0.tar.gz',
    keywords=['python', 'physics', 'numbers', 'math'],
    classifiers=[],
    cmdclass=cmdclass,
    ext_modules=ext_modules
)
