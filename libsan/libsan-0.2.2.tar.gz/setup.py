from __future__ import absolute_import, division, print_function, unicode_literals
import sys
import platform
from setuptools import setup, find_packages
from distutils.util import convert_path

distro_name = platform.linux_distribution()[0]
try:
    distro_version = platform.linux_distribution()[1]
    distro_version = float(distro_version)
except TypeError:
    print("Could not get version of distribution, got %s" % distro_version)
    distro_version = 0.0

install_requires = ['paramiko']
setup_requires = ['pytest-runner']

if distro_name == "Red Hat Enterprise Linux Server":
    # On RHEL newer version of paramiko does not build
    install_requires = ["paramiko==1.7.5"]
    # pytest requires setuptools version > 12
    if distro_version <= 8.0:
        setup_requires = []

# install argparse if python < 2.7, since 2.7 argparse is included on standard lib
if sys.hexversion < 0x02070000:
    install_requires.extend(['argparse', 'ipaddress'])
    setup_requires = []

install_requires.extend(['python-augeas', 'future', 'six', 'distro', 'netifaces'])

main_ns = {}
ver_path = convert_path('libsan/_version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

setup(name='libsan',
      description='Python modules to manage SAN devices',
      version=main_ns['__version__'],
      license='GPLv3+ (see LICENSE)',
      packages=find_packages(exclude=['bin', 'tests']),
      # packages=['libsan', 'libsan/host', 'libsan/switch', 'libsan/switch/cisco',
      #           'libsan/switch/brocade', 'libsan/physwitch', 'libsan/physwitch/apcon',
      #           'libsan/array', 'libsan/misc', 'libsan/array/dell',
      #           'libsan/array/linux', 'libsan/array/netapp', 'libsan/array/emc'],
      install_requires=install_requires,
      setup_requires=setup_requires,
      dependency_links=['https://github.com/PythonCharmers/python-future/archive/master.zip?ref=master#egg=future',
                        'https://github.com/nir0s/distro/archive/master.tar.gz?ref=master#egg=distro'],
      # data_files=[('/etc', ['sample_san_top.conf'])],
      scripts=['bin/sancli'],
      tests_require=['pytest'],
      test_suite='tests',
      url='https://gitlab.com/rh-kernel-stqe/python-libsan.git',
      author='Bruno Goncalves',
      author_email='bgoncalv@redhat.com',
      # long_description=open("README.md").read()
      )
