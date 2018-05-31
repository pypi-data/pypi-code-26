import io

from setuptools import setup


with io.open('README.rst', 'rt', encoding='utf8') as f:
    readme = f.read()


setup(
    name='flask-contentful',
    version='0.0.2',
    url='https://github.com/eillarra/flask-contentful',
    author='eillarra',
    author_email='eneko@illarra.com',
    license='MIT',
    description='',
    long_description=readme,
    keywords='flask contentful',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    packages=['flask_contentful'],
    install_requires=[
        'contentful',
        'flask',
        'markdown',
    ],
    zip_safe=False
)
