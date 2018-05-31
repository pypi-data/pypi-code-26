from functools import partial
from .catalog import catalog
from .root import Root
from ..utils import cached_property


class Result:
    def __init__(self, tasks):
        self.tasks = tasks
        self.filters = []
        self.dirty = True

    def _check_name(self, name, task):
        # filter only last task results
        if name is None:
            return task.name == self.tasks.tail.name
        # filter results by task name
        if isinstance(name, str):
            return task.name == name
        # filter results by task names list
        if isinstance(name, (list, tuple)):
            return task.name in name
        raise TypeError('invalid name type')

    def filter(self, condition=None):
        if isinstance(condition, (str, list, tuple)) or condition is None:
            condition = partial(self._check_name, condition)
        self.filters.append(condition)
        # self.dirty = True   # invalidate cache
        return self

    def all(self):
        self.filters = []

    def __iter__(self):
        # update cache
        if self.dirty:
            self.tasks.run()
            self.dirty = False
        # get results from tasks
        for task in self.tasks:
            # drop if output disabled
            if not task.debug:
                continue
            # drop if some check from filters not passed
            for check in self.filters:
                if not check(task):
                    break
            else:
                yield from task.results

    def __repr__(self):
        state = 'Dirty' if self.dirty else 'Cached'
        return '{}Result({} filters)'.format(state, len(self.filters))


class Chain:
    def __init__(self, task):
        self.head = task        # left task in chain
        self.tail = task        # right task in chain

    @cached_property
    def root(self):
        root = Root()
        root.add(self.head)
        return root

    @cached_property
    def result(self):
        return Result(self)

    def __or__(self, other):
        self.tail.add(other.head)
        self.tail = other.head
        self.result.dirty = True    # invalidate cache
        return self

    @classmethod
    def _chain(cls, task):
        yield task
        if task.subtasks:
            yield from cls._chain(task.subtasks[0])

    def __iter__(self):
        return self._chain(self.root)

    def run(self):
        self.root.run()
        return self

    def __str__(self):
        if self.head == self.tail:
            return self.head.name
        return '{} -> ... -> {}'.format(self.head.name, self.tail.name)

    def __repr__(self):
        return 'Chain({})'.format(self)


def task(command, task_name=None, *, args=None, output=True, **kwargs):
    if args and kwargs:
        raise ValueError('do not use args with **kwargs')
    # get command by name
    if isinstance(command, str):
        command = catalog.get(command)
    task = command(debug=output)
    if task_name is not None:
        task.name = task_name
    task.args.update(kwargs)
    if args:
        task.args.update(args)
    return Chain(task)


def chain(root_task, *other_tasks):
    for task in other_tasks:
        root_task.__or__(task)
    return root_task.get()
