from setuptools import setup


setup(
    name='fdate',
    version=__import__('fdate').__version__,
    description="Formats date string as 'yyyy-mm-dd' and manipulates dates.",
    long_description=open("README.md").read(),
    author='qx3501332',
    author_email='x.qiu@qq.com',
    license="MIT License",
    url='https://github.com/nullgo/fdate',
    packages=['fdate'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    zip_safe=False,
)