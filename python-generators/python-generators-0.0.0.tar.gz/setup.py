import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="python-generators",
    version="0.0.0",
    author="Ruan Herculano",
    author_email="ruannawe@gmail.com",
    description="A simple lib that prints out a random Taylor Swift lyric",
    long_description=long_description,
    # long_description_content_type="text/markdown",
    url='https://github.com/RuanHerculano/python-generators',
    download_url='https://github.com/RuanHerculano/python-generators.git',
    keywords=['python', 'generators', 'crud generator'],  # arbitrary keywords
    # packages=setuptools.find_packages(),
    packages=['tay_say_test'],  # this must be the same as the name above
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points={'console_scripts': ['tay_say_test=tay_say_test:print_lyric']},
)
