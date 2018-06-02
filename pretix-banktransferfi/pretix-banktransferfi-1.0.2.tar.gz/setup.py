import os
from distutils.command.build import build

from django.core import management
from setuptools import setup, find_packages


try:
    with open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ''


class CustomBuild(build):
    def run(self):
        management.call_command('compilemessages', verbosity=1, interactive=False)
        build.run(self)


cmdclass = {
    'build': CustomBuild
}


setup(
    name='pretix-banktransferfi',
    version='1.0.2',
    description='Pretix plugin that creates a reference number (viitenumero) compliant with Finnish banks.',
    long_description=long_description,
    url='https://github.com/fmorato/pretix-banktransferfi',
    author='Felipe Morato',
    author_email='me@fmorato.com',
    license='Apache Software License',

    install_requires=[],
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    cmdclass=cmdclass,
    entry_points="""
[pretix.plugin]
banktransferfi=pretix_banktransferfi:PretixPluginMeta
""",
)
