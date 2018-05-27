import setuptools

# Try to create an rst long_description from README.md
try:
    args = 'pandoc', '--to', 'rst', 'README.md'
    long_description = subprocess.check_output(args)
    long_description = long_description.decode()
except Exception as error:
    print('README.md conversion to reStructuredText failed. Error:')
    print(error)
    print('Setting long_description to None.')
    long_description = None

cur_classifiers = [
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Topic :: Software Development :: Libraries",
    "Topic :: Utilities",
]

setuptools.setup(
    name="ppl",
    version="0.0.4",
    author='Abin Simon',
    author_email='abinsimon10@gmail.com',
    description="A pretty progressbar library",
    url="https://github.com/meain/ppl",
    long_description=long_description,
    packages=setuptools.find_packages(),
    keywords=['progressbar', 'spinner', 'loader'],
    classifiers=cur_classifiers)
