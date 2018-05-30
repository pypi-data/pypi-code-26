from jinja2 import PackageLoader, Environment, FileSystemLoader

from star_builder.build import Command, find_tasks
from src.paas_star.build.tasks import Backend


class UnionEnv(object):

    def __init__(self, *args):
        self.envs = args

    def __getattr__(self, item):

        def inner(*args, **kwargs):
            ex = None
            for env in self.envs:
                try:
                    return getattr(env, item)(*args, **kwargs)
                except Exception as e:
                    ex = e
                    pass
            raise ex
        return inner


class PaasCommand(Command):

    def __init__(self, tasks):
        tasks["backend"] = Backend
        super(PaasCommand, self).__init__(tasks)

    def create(self):
        if self.templates_path:
            env = Environment(loader=FileSystemLoader(self.templates_path))
        else:
            env = UnionEnv(
                Environment(loader=PackageLoader('star_builder', 'templates')),
                Environment(loader=PackageLoader('paas_star', 'templates')))
        self.task.create(env, **vars(self.args))


def main():
    PaasCommand(find_tasks()).create()
