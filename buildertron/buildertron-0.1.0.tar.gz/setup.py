#
# buildertron
#
import subprocess
from setuptools import setup, find_packages, Command

from info import (__projectname__, __version__, __homepage__, __author__,
                  __classifiers__, __readme__, __history__, __description__,
                  __author_email__)


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        return

    def finalize_options(self):
        return

    def run(self):
        subprocess.call(['flake8', '--append-config=.flake8.ini'])


cmd_classes = {
    'test': TestCommand,
}


setup(name=__projectname__,
      version=__version__,
      description=__description__,
      long_description=__readme__ + '\n\n' + __history__,
      author=__author__,
      author_email=__author_email__,
      url=__homepage__,
      license='MIT',
      packages=find_packages(exclude=['docs', 'resources', 'snap', 'tests*']),
      package_data={'': ["icons/*.png", "splash.png", "buildertron.png"]},
      data_files=[('share/applications', ['data/Buildertron.desktop']),
                  ('share/buildertron', ['buildertron/buildertron.png'])],
      install_requires=["pyqt5"],
      classifiers=__classifiers__,
      test_suite='tests',
      tests_require=[],
      cmdclass=cmd_classes,
      entry_points={'gui_scripts': ['buildertron = buildertron.buildertron:main']}
      )
