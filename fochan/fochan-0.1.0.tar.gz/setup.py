import os.path
import warnings
import sys
from distutils.spawn import spawn
import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

DESCRIPTION = '4chan thread downloader'
LONG_DESCRIPTION = 'Command-line program to download 4chan threads'

files_spec = [
    ('etc/bash_completion.d', ['fochan.bash-completion']),
    ('etc/fish/completions', ['fochan.fish']),
    ('share/doc/fochan', ['README.md']),
    ('share/man/man1', ['fochan.1'])
]

root = os.path.dirname(os.path.abspath(__file__))

data_files = []

for dirname, files in files_spec:
    resfiles = []
    for fn in files:
        if not os.path.exists(fn):
            warnings.warn('Skipping file %s since it is not present. Type make to build all automatically generated files.' % fn)
        else:
            resfiles.append(fn)
    data_files.append((dirname, resfiles))

params = {
    'data_files': data_files,
}

params['entry_points'] = {'console_scripts': ['fochan = fochan:main']}


class build_lazy_extractors(setuptools.Command):
    description = 'Build the extractor lazy loading module'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        spawn(
            [sys.executable, 'devscripts/make_lazy_extractors.py', 'fochan/extractor/lazy_extractors.py'],
            dry_run=self.dry_run,
        )


setuptools.setup(
    name="fochan",
    version="0.1.0",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author="Maroof",
    author_email="i@imrfgl.me",
    url="https://github.com/mrfgl/fochan",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    cmdclass={'build_lazy_extractors': build_lazy_extractors},
    **params
)
