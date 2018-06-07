import os.path
from glob import glob

from bricks.plugin_kit.base import BasePlugin
from bricks.plugin_kit.steps.file_ops import FileRender
from bricks.plugins.resources.python_library import (setup_py_template,
                                                     requirements_dev,
                                                     setup_cfg,
                                                     default_test_py)

reference = {
    'test': "Runs the tests from tests/ using pytest.",
    'lint': "Check code quality using pycodestyle (formerly pep8)",
    'release-patch': "Increments the patch (x.y.Z) version and "
                     "builds the new dists",
    'release-minor': "Increments the minor (x.Y.z) version and "
                     "builds the new dists",
    'release-major': "Increments the major (X.y.z) version and "
                     "builds the new dists",
    'upload': "Uploads the last built packages to PiPy "
              "(you should run a release-* command before)"
}


class Plugin(BasePlugin):
    reference = reference

    def __init__(self, project):
        super(Plugin, self).__init__(project)

    def get_commands(self):
        return [
            self.build_command(
                commands=['pytest tests/'],
                name='test',
                driver='local'
            ),
            self.build_command(
                name='lint',
                driver='local',
                commands=['pycodestyle']
            ),
            self.make_release_command('patch'),
            self.make_release_command('minor'),
            self.make_release_command('major'),
            self.get_twine_upload_command()
        ]

    def make_release_command(self, kind):
        return self.build_command(
            name='release-{}'.format(kind),
            driver='local',
            commands=[
                'bumpversion {}'.format(kind),
                'python setup.py sdist bdist_wheel',
            ]
        )

    def initialize(self):
        project_name = self.project.metadata.name
        return [
            FileRender('setup.py', setup_py_template),
            FileRender(os.path.join(project_name, '__init__.py'), ''),
            FileRender('requirements.txt', requirements_dev),
            FileRender('setup.cfg', setup_cfg),
            FileRender(os.path.join('tests', '__init__.py'), ''),
            FileRender(os.path.join('tests', 'test_default.py'),
                       default_test_py),
        ]

    def get_twine_upload_command(self):
        version = self.project.metadata.version
        filenames = glob('dist/*{}*'.format(version))
        return self.build_command(
            name='upload',
            driver='local',
            commands=['twine upload ' + ' '.join(filenames)]
        )
