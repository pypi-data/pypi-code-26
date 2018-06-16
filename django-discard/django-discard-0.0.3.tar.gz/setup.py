import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='django-discard',
    version='0.0.3',
    packages=setuptools.find_packages(),
    include_package_data=True,
    license='MIT License',
    description='A simple package to add discard (soft-delete) functionality to\
                 desired models',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/tcostam/django-discard',
    author='Tiago Melo',
    author_email='to_be_provided@email.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'
    ],
)