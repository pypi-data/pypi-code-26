# Don't import __future__ packages here; they make setup fail
import os

# First, we try to use setuptools. If it's not available locally,
# we fall back on ez_setup.
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

with open("README.pypi.rst") as readmeFile:
    long_description = readmeFile.read()

install_requires = []
with open("requirements.txt") as requirementsFile:
    for line in requirementsFile:
        line = line.strip()
        if len(line) == 0:
            continue
        if line[0] == '#':
            continue
        pinnedVersion = line.split()[0]
        install_requires.append(pinnedVersion)

dependency_links = []
try:
    with open("constraints.txt") as constraintsFile:
        for line in constraintsFile:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] == '#':
                continue
            dependency_links.append(line)
except EnvironmentError:
    print('No constraints file found, proceeding without '
          'creating dependency links.')


setup(
    name="sheepdog-exporter",
    description="Export metadata from the DCP Sheepdog API.",
    packages=["sheepdog_exporter"],
    url="https://github.com/david4096/sheepdog-exporter",
    entry_points={
        'console_scripts': [
            'sheepdog-exporter=sheepdog_exporter.sheepdog_exporter:main'
        ]
    },
    long_description=long_description,
    install_requires=install_requires,
    dependency_links=dependency_links,
    license='Apache License 2.0',
    include_package_data=True,
    zip_safe=True,
    author="David Steinberg",
    author_email="davidcs@ucsc.edu",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    version='0.3.0',
    keywords=['genomics', 'metadata', 'NIHDataCommons'],
    # Use setuptools_scm to set the version number automatically from Git
)

