from setuptools import setup


setup(
    name='bloodyterminal',
    packages=['bloodyterminal'],
    version='3.1',
    description='A little helper to structure your terminal output',
    long_description=open('README.rst', encoding="utf8").read(),
    author='TheBloodyScreen',
    author_email='jaydee@thebloodyscreen.com',
    license='MIT',
    classifiers=[
                'Development Status :: 3 - Alpha',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: MIT License',
                'Programming Language :: Python :: 3.6'
    ],
    install_requires=['colorama'],
    url='https://github.com/TheBloodyScreen/bloodyterminal/'
)
