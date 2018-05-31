from .command import Command
from .catalog import catalog


@catalog.register
class Root(Command):
    name = 'root'
    implement = {'root'}

    def entrypoint(self):
        for subtask in self.subtasks:
            subtask = subtask.entrypoint()
            subtask.send(None)
            subtask.send((self, 0))

    def run(self):
        return self.entrypoint()
