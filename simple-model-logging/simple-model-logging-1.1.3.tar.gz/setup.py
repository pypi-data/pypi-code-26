from setuptools import find_packages, setup


version = '1.1.3'


# install_requires={
# }


setup(
    name='simple-model-logging',
    packages=['simple_model_logging'],
    include_package_data=True,
    version=version,
    description='Based Django 2.0.4  to logging update',
    long_description=open('README.md').read(),
    author='Jason Jiang',
    author_email='jiangjun0130@aliyun.com',
    url='https://github.com/jiangjun0130/simple-model-logging',
    # install_requires=install_requires,
    extras_require={},
    zip_safe=False,
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries',
    ],
)
