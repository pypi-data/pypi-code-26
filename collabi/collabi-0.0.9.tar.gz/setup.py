from setuptools import setup, find_packages

import collabi

setup(
    name='collabi',
    version=collabi.__version__,
    description=collabi.__doc__.strip(),
    long_description='more stuff',
    url='https://github.com/UnityTech/unitycloud-collab-cli',
    author=collabi.__author__,
    author_email='collabsupport@unity3d.com',
    license=collabi.__license__,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'collabi = collabi.__main__:main',
        ],
    },
    install_requires=[
        'python-dateutil==2.7.3',
        'requests==2.18.4',
        'grequests==0.3.0',
        'humanize==0.5.1',
        'tabulate==0.8.2',
        'send2trash==1.5.0',
        'tqdm==4.23.4',
        'keyring==12.2.1',
        'filelock==3.0.4'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development',
        'Topic :: Terminals',
        'Topic :: Utilities'
    ],
)
