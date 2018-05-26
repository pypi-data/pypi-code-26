import os

from setuptools import setup, find_packages


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def _open(*path):
    return open(os.path.join(PROJECT_DIR, *path))


def _get_version():
    with _open('dictmatching', '__init__.py') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[-1].strip().strip('\'')


def _read(*path):
    with _open(*path) as f:
        return f.read()


def main():
    return setup(
        name='dictmatching',
        description='Unpacking dicts is now easier than ever',
        packages=find_packages(exclude=['tests']),
        version=_get_version(),
        long_description=_read('README.rst'),
        include_package_data=True,
        python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
        url='https://github.com/yehonatanz/dictmatching',
        author='yehonatanz',
        install_requires=[
            'decorator',
            'six',
        ],
        classifiers=(
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
        )
    )


if __name__ == '__main__':
    main()
