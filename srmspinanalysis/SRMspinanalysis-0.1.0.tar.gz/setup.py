from setuptools import setup
from codecs import open
from os import path
import sys

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'SRMspinanalysis', '_version.py')) as version_file:
    exec(version_file.read())

with open(path.join(here, 'README.md')) as readme_file:
    readme = readme_file.read()

with open(path.join(here, 'CHANGELOG.md')) as changelog_file:
    changelog = changelog_file.read()

desc = readme + '\n\n' + changelog
try:
    import pypandoc
    long_description = pypandoc.convert_text(desc, 'rst', format='md')
    with open(path.join(here, 'README.rst'), 'w') as rst_readme:
        rst_readme.write(long_description)
except (ImportError, OSError, IOError):
    long_description = desc

install_requires = [
    'numpy',
    'beautifulsoup4',
    'regex',
    'scipy',
    'matplotlib',
]

tests_require = [
    'pytest',
    'pytest-cov',
]

needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
setup_requires = ['pytest-runner'] if needs_pytest else []

setup(
    name='SRMspinanalysis',
    version=__version__,
    description='Spin-stabilization Analysis for Solid Rocket Motor Systems',
    long_description=long_description,
    author='Matthew D. Morse',
    author_email='morse.mattd@gmail.com',
    url='https://github.com/SoftwareDevEngResearch/SRMspinanalysis',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
    ],
    license='MIT',
    install_requires=install_requires,
    tests_require=tests_require,
    python_requires='>=2',
    setup_requires=setup_requires,
    zip_safe=False,
    packages=['SRMspinanalysis', 'SRMspinanalysis.tests'],
    package_dir={
        'SRMspinanalysis': 'SRMspinanalysis',
        'SRMspinanalysis.tests': 'SRMspinanalysis/tests',
        },
    include_package_data=True,
    )

if __name__ == "__main__":
    setup()