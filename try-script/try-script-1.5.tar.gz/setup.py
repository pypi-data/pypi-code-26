from setuptools import setup

VERSION = '1.5'

setup(
    name='try-script',
    packages=['try_pkg'],
    version=VERSION,
    description='Just script that helps me learn foreign languages,',
    author='Jan Kaifer',
    author_email='kaifer741@gamil.com',
    url='https://github.com.jankaifer/app.py',
    keywords=['learning', 'school', 'german', 'english', 'awesome'],
    classifiers=[],
    entry_points={
        'console_scripts': [
            'try = try_pkg.app:main',
        ],
    }
)
