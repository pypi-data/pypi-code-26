from setuptools import setup

with open('README.md', 'rt', encoding='utf8') as f:
    readme = f.read()

setup(
    name='lektor-bibtex-support',
    version='0.1.1',
    author='Arun Persaud',
    author_email='arun@nubati.net',
    description = 'Bibtex file support to easily include publication lists.',
    long_description=readme,
    long_description_content_type='text/markdown',
    data_files=[('templates', ['templates/lektor_bibtex_support_default_template.html'])],
    url='https://github.com/arunpersaud/lektor-bibtex-support',
    include_package_data=True,
    keywords='Lektor plugin static-site bibtex',
    license='MIT',
    py_modules=['lektor_bibtex_support'],
    entry_points={
        'lektor.plugins': [
            'bibtex-support = lektor_bibtex_support:BibtexSupportPlugin',
        ]},
    install_requires=['pybtex'],
    classifiers=[
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Framework :: Lektor',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
