import fnmatch
from collections import namedtuple
from .catalog import catalog
from .root import Root
from .loader import Loader


TreeElement = namedtuple('TreeElement', ['deepth', 'task', 'is_pointer'])


class Tree:
    def __init__(self, logger):
        self.root = Root()
        self.pointer = self.root
        self.logger = logger
        self.loader = Loader

    def _get_parent(self, task=None, parent=None):
        if task is None:
            task = self.pointer
        if parent is None:
            parent = self.root
        if task in parent.subtasks:
            return parent
        for subtask in parent.subtasks:
            result = self._get_parent(task, subtask)
            if result:
                return result
        if parent == self.root:
            self.logger.error('parent for task not found')

    def _get_task_by_name(self, name):
        for el in self.tree():
            if el.task.name == name:
                return el.task
        self.logger.error('task not found')

    def tree(self, task=None):
        if task is None:
            task = self.root
        is_pointer = (task is self.pointer)
        result = [TreeElement(0, task, is_pointer)]
        for subtask in task.subtasks:
            subtree = [el._replace(deepth=el.deepth + 1) for el in self.tree(subtask)]
            result.extend(subtree)
        return result

    def push(self, command, *args):
        task = command()
        self.pointer.add(task)
        self.pointer = task
        self.logger.info('pushed')
        if args:
            self.args(*args)
        return True

    def pop(self, task=None):
        if task is None:
            task = self.pointer
        self.pointer = self._get_parent(task)
        if self.pointer is None:
            return False
        self.pointer.subtasks = [cmd for cmd in self.pointer.subtasks if cmd is not task]
        self.logger.info('poped')
        return True

    def goto(self, task):
        for el in self.tree():
            if el.task is task:
                self.pointer = task
                return True
        self.logger.error('task not found in tree')
        return False

    def reset(self, *args):
        self.root = Root()
        self.pointer = self.root
        self.logger.info('reseted')
        return True

    def rename(self, task=None, name=None):
        if type(task) is str and name is None:
            task, name = name, task
        if name is None:
            self.logger.error('new name required')
            return False
        if task is None:
            task = self.pointer
        task.name = name
        self.logger.info('renamed')
        return True

    def args(self, *args):
        task = self.pointer
        return task.update_args(args)

    def sources(self, *sources):
        task = self.pointer
        task.sources = set(sources)
        self.logger.info('sources changed')
        return True

    def flush(self, task=None):
        if task is None:
            task = self.pointer
        task.flush()
        self.logger.info('flushed')
        return True

    def describe(self, task=None):
        if task is None:
            task = self.pointer
        return task.describe()

    def load(self, path):
        exists = set(catalog)
        # file
        if path.endswith('.py'):
            is_loaded = self.loader.load_file(path)
            if not is_loaded:
                self.logger.error('file not found')
                return []
        # module name
        else:
            is_loaded = self.loader.load_module(path)
            if not is_loaded:
                self.logger.error('module not found')
                return []
        # return list of loaded tasks
        loaded = set(catalog) - exists
        if loaded:
            self.logger.info('loaded')
        else:
            self.logger.warning('loaded 0 tasks')
        return sorted(list(loaded))

    def list(self, pattern=None):
        result = list(catalog)
        if pattern:
            result = fnmatch.filter(names=result, pattern=pattern)
        if not result:
            self.logger.warning('no matches found')
        return sorted(result)

    def run(self):
        self.root.run()

    def pause(self):
        ...

    def stop(self):
        ...
