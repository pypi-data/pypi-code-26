from setuptools import setup, find_packages

import collabi

with open('requirements.txt') as f:
    requirements = f.readlines()

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
    install_requires=requirements,
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
