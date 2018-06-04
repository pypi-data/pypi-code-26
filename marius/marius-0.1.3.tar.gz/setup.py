from setuptools import setup

setup(
    name='marius',
    packages=['marius', 'marius.core', 'marius.helper'],
    version='0.1.3',
    url='https://github.com/Jack-Kingdom/marius.git',
    description='Light weight job scheduling tool with more performance and scalability.',
    long_description=open('README.md').read(),

    author='Jack King',
    author_email='email@qiaohong.org',
    license='MIT',

    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Natural Language :: English',
    ],
)
