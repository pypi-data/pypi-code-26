from sklearn_porter import Porter
from sklearn.externals import joblib
from mako.template import Template
import os

from sklearn2gem.templates import *


def capitalize(s):
    return s[0].upper() + s[1:]


def get_class_name(s):
    w = [capitalize(x) for x in s.split('_')]
    return ''.join(w)


class SklearnGemGenerator(object):
    """Generate necessary files."""

    def __init__(self, gem_name, version, pkl_path):
        self.name = gem_name
        self.version = version
        self.clf = joblib.load(pkl_path)

    def generate(self, destination):
        if not os.path.exists(destination):
            os.mkdir(destination)
        if not os.path.isdir(destination):
            raise Exception("The destination has to be a directory")
        if len(os.listdir(destination)) > 0:
            raise Exception("The destination directory is not empty")

        context = {
            'gem_name': self.name,
            'class_name': get_class_name(self.name),
            'n_features': self.clf.n_features_,
            'version': self.version,
        }

        os.mkdir(f'{destination}/lib')
        os.mkdir(f'{destination}/ext')
        os.mkdir(f'{destination}/ext/{self.name}')

        with open(f'{destination}/{self.name}.gemspec', 'w') as f:
            f.write(GEMSPEC.render(**context))

        with open(f'{destination}/Rakefile', 'w') as f:
            f.write(RAKEFILE.render(**context))

        with open(f'{destination}/lib/{self.name}.rb', 'w') as f:
            f.write(INIT_RB.render(**context))

        with open(f'{destination}/ext/{self.name}/{self.name}.c', 'w') as f:
            f.write(BINDING_C.render(**context))

        with open(f'{destination}/ext/{self.name}/extconf.rb', 'w') as f:
            f.write(EXTCONF_RB.render(**context))

        porter = Porter(self.clf, language='c', method='predict')
        with open(f'{destination}/ext/{self.name}/sklearn_model.c', 'w') as f:
            f.write(porter.export(embed_data=True))
