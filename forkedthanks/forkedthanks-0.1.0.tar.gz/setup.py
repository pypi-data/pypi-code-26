from setuptools import setup
from setuptools import find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = [
    'pygithub>=1.39',
    'click>=6.7',
    'hues>=0.2.2'
]

setup(
    name='forkedthanks',
    version='0.1.0',
    description="Thanks with a ⭐️ the projects you forked",
    long_description=readme,
    author="Etienne Napoleone",
    author_email='etienne_napo@hotmail.com',
    # download_url=
    url='https://github.com/etienne-napoleone/forkedthanks',
    project_urls={
        'Source': 'https://github.com/etienne-napoleone/forkedthanks',
        'Tracker': 'https://github.com/etienne-napoleone/forkedthanks/issues',
    },
    packages=['forkedthanks'],
    entry_points={
        'console_scripts': [
            'forkedthanks=forkedthanks.forkedthanks:main',
        ],
    },
    python_requires='>=3.5',
    install_requires=requirements,
    license="MIT License",
    keywords='forkedthanks',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Environment :: Console',
        'Topic :: Software Development :: Version Control :: Git',
        'Topic :: Utilities'
    ],
)
