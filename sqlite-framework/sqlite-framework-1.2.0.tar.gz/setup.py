from setuptools import setup, find_packages

from sqlite_framework import project_info

setup(
    name=project_info.name,

    use_scm_version=True,

    description=project_info.description,
    long_description=project_info.description,

    url=project_info.url,

    author=project_info.author_name,
    author_email=project_info.author_email,

    license=project_info.license_name,

    packages=find_packages(exclude=["sqlite_framework_test*"]),

    setup_requires=[
        'setuptools_scm',
        'wheel'
    ],

    install_requires=[
    ],

    python_requires='>=3',

    # for pypi:

    keywords='sqlite framework sqlite3 sql database',

    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Database',
        'Programming Language :: SQL',

        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
)
