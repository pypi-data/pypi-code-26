import json
import logging
import os
import unittest
import creaturecast_project.data.project_objects as dmd
import creaturecast_project.data.projects as ses

directory = os.path.dirname(__file__.replace('\\', '/'))

with open('%s/animals.json' % directory, mode='r') as f:
  animals = json.load(f)

with open('%s/dinosaurs.json' % directory, mode='r') as f:
  dinosaurs = json.load(f)

with open('%s/movies.json' % directory, mode='r') as f:
  movies = json.load(f)

with open('%s/names.json' % directory, mode='r') as f:
  names = json.load(f)


class DataTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(DataTest, self).__init__(*args, **kwargs)
        self.log = logging.getLogger(self.__class__.__name__)

    def test_creation(self):

        for movie_name in movies[0:22]:
            project = dmd.Project(
                name=movie_name['name'],
                icon='folder'
            )
            for animal in animals[0:22]:
                asset = dmd.Asset(
                    name=animal,
                    project=project,
                    icon='folder_user'
                )
                for component_name in ['rig', 'model', 'texture']:
                    component = dmd.Component(
                        name=component_name,
                        asset=asset,
                        icon='polygon'
                    )
                    for version_number in range(12):
                        component_version = dmd.ComponentVersion(
                            version=version_number,
                            component=component,
                            icon='polygon',
                            name='%s_v%s' % (component_name, version_number)
                        )

            ses.session.add(project)
            ses.session.commit()
            print movie_name



if __name__ == '__main__':
    unittest.main()
