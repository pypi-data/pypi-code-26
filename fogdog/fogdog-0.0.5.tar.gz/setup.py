from setuptools import setup


setup(
    name='fogdog',
    version=__import__('fogdog').__version__,
    description="fogdog",
    author='qx3501332',
    author_email='x.qiu@qq.com',
    license="MIT License",
    url='https://github.com/nullgo/fogdog',
    packages=['fogdog'],
    include_package_date=True,
    zip_safe=True,
    install_requires=['numpy', 'scipy'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
