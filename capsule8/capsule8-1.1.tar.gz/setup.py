import os
import sys
from setuptools import setup, Command
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''

    def run_tests(self):
        import shlex
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('rm -rf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')


setup(
    name='capsule8',
    version="1.1",
    description="capsule8 open source sensor python grpc bindings",
    author='Alexander Comerford',
    author_email='alex@capsule8.com',
    url='http://github.com/capsule8/api-python',
    install_requires=["grpcio",
                      "grpcio-tools",
                      "google-api-python-client",
                      "googleapis-common-protos"],
    test_requires=["pytest"],
    packages=["capsule8", "capsule8.api", "capsule8.api.v0"],
    cmdclass={
        'clean': CleanCommand,
        'test': PyTest
    }
)
