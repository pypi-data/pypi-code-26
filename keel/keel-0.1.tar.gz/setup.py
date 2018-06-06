import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name="keel",
    packages=setuptools.find_packages(),
    version='0.1',
    description='Kill proccesses effectively and easily',
    author='Anguel Hristozov',
    author_email='angel.hristozov@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/modelorona/keel',
    # download_url='https://github.com/modelorona/keel/archive/0.1.tar.gz',
    keyword=['kill', 'process', 'easy'],
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Environment :: Console :: Curses',
        'Natural Language :: English'
    )
)
