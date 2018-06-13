from setuptools import setup

with open("README.md", "r") as fh:
    readme = fh.read()

requirements = [
]

test_requirements = [
]

setup(
    name='pyfacy_dlib_models',
    version='0.0.2',
    description="Models used by the pyfacy package.",
    long_description=readme,
    author="Manivannan Murugavel",
    author_email='manivannanmca2012@gmail.com',
    url='https://github.com/ManivannanMurugavel/pyfacy_dlib_models',
    packages=[
        'pyfacy_dlib_models',
    ],
    package_dir={'pyfacy_dlib_models': 'pyfacy_dlib_models'},
    package_data={
        'pyfacy_dlib_models': ['models/*.dat']
    },
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='pyfacy',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)