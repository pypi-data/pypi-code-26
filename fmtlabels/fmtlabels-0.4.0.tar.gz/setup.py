from setuptools import setup

setup(
    name='fmtlabels',
    version='0.4.0',
    description='labels formatting from csv/xlsx to json',
    url='http://bitbucket.org/yimian/fmtlabels',
    packages=['fmtlabels'],
    python_requires='>=3.5',
    install_requires=[
        'tablib>=0.12',
        'requests>=2.18',
    ],
    scripts=['bin/fmttab', 'bin/fmtlines', 'bin/cntaspect'],
    zip_safe=False
)
