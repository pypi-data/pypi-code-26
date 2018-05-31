import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="itunesmusicsearch",
    version="0.0.1",
    author="Andrii Smirnov",
    author_email="andrew.fonrims@gmail.com",
    description="A small iTunes API wrapper (made for test task)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fonrims/itunesmusicsearch",
    packages=['itunesmusicsearch'],
    install_requires=['requests>=2.8'],
    license='MIT',
    classifiers=(
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
    ),
)