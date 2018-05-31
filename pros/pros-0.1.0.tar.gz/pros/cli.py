from functools import partial
from inspect import getargspec

from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.contrib.completers import WordCompleter
# from prompt_toolkit import print_formatted_text, HTML

from .core import Tree, commands, Loader
from .logger import logger


Loader.load_all()

DEBUG = True


class ProxyTree:
    def __init__(self, logger):
        self._tree = Tree(logger)

    def getter(self, name, *args):
        method = getattr(self._tree, name)

        # replace task name to task object
        if args:
            argspec = getargspec(method).args
            if len(argspec) >= 2 and argspec[1] == 'task':
                task = self._tree._get_task_by_name(args[0])
                if task is None:
                    self._tree.logger.error('task not found')
                    return
                args[0] = task

        # call method
        result = method(*args)
        if isinstance(result, list):
            result = '\n'.join(result)
        return result

    def __getattr__(self, name):
        return partial(self.getter, name)

    def push(self, command_name, *args):
        if command_name not in commands:
            self._tree.logger.error('command not found')
            return
        command = commands[command_name]
        return self._tree.push(command, *args)

    def tree(self):
        tree = self._tree.tree()
        result = []
        for el in tree:
            line = ['-' * el.deepth * 2, el.task.name]
            if el.task.sources:
                line.extend(['[', ', '.join(sorted(el.task.sources)), ']'])
            if el.is_pointer:
                line.append(' <--- you are here')
            result.append(''.join(line))
        return '\n'.join(result)


ACTIONS = tuple(action for action in dir(Tree) if not action.startswith('_'))
COMMANDS = tuple(commands.keys())

tree = ProxyTree(logger=logger)
history = InMemoryHistory()
suggest = AutoSuggestFromHistory()
completer = WordCompleter(ACTIONS + COMMANDS)


def cli():
    while 1:
        try:
            text = prompt('> ', history=history, auto_suggest=suggest, completer=completer)
        except KeyboardInterrupt:
            print('Bye!')
            return
        if not text:
            continue
        action, *args = text.split()

        try:
            result = getattr(tree, action)(*args)
        except Exception as e:
            if DEBUG:
                raise
            logger.critical(e)
            continue

        if result is not None and type(result) is not bool:
            print(result)


if __name__ == '__main__':
    cli()
