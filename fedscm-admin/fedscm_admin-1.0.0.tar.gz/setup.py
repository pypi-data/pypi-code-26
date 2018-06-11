from setuptools import setup

description = \
    'A CLI tool to issue tickets for repo requests'

setup(
    author='Red Hat, Inc.',
    author_email='mprahl@redhat.com',
    data_files=[('/etc/fedscm-admin/', ['config.ini'])],
    description=description,
    entry_points='''
        [console_scripts]
        fedscm-admin=fedscm_admin.fedscm_admin:cli
    ''',
    include_package_data=True,
    install_requires=['click', 'python-bugzilla', 'python-fedora', 'pyyaml',
                      'requests', 'six'],
    license='GPLv2+',
    name='fedscm_admin',
    packages=['fedscm_admin'],
    package_dir={'fedscm_admin': 'fedscm_admin'},
    url='https://pagure.io/fedscm_admin',
    version='1.0.0',
)
