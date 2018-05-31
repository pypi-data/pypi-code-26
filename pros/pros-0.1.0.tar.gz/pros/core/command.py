from argparse import ArgumentParser


class Command:
    """
    class    | command | some actions set. Get massages and generate new messages.
    instance | task    | one node of tree. Command, prepared to execution.
    """
    name = None
    implement = frozenset()     # implemented protocols: http, grep, facebook...
    sources = frozenset()       # source messages protocols

    def __init__(self, debug=False):
        self.flush()
        self.debug = debug
        if debug:
            self.results = []

    def flush(self):
        """Flush task to default params from command.
        """
        self.subtasks = []
        self.args = {}
        if self.__class__.name is None:
            raise ValueError('name can not be None')
        self.name = self.__class__.name
        self.parser = self.get_parser(ArgumentParser(
            prog='args',
            description=self.__doc__,
            add_help=False,
        ))
        self.update_args([])    # set default args

    def entrypoint(self):
        """entrypoint for task.

        Do not redefine it into childs!

        * init subtasks entrypoints,
        * init current `process`,
        * propagate messages to subtasks,
        * send messages to `process`,
        * send messages from `process` to subtasks.
        """
        subtasks = []
        for subtask in self.subtasks:
            # point to entrypoint
            subtask = subtask.entrypoint()
            # go to first yield
            subtask.send(None)
            # save generator to list
            subtasks.append(subtask)

        # get generator for proccess and go to first yield
        process = self.process(**self.args)
        process.send(None)

        while 1:
            # get message from parent
            input_message = yield
            if input_message is None:
                break
            source, input_message = input_message
            assert input_message is not None, "message can not be None"

            # propagate input_message to subtasks
            for subtask in subtasks:
                if self.filter_propagation(source, input_message):
                    subtask.send((source, input_message))

            # check if message must be ignored
            if not self.filter_processing(source, input_message):
                continue

            # send message to current process
            output_message = process.send((source, input_message))

            # send messages from current process to subtasks
            while output_message is not None:
                if self.debug:
                    self.results.append(output_message)
                for subtask in subtasks:
                    subtask.send((self, output_message))
                try:
                    output_message = process.send(None)
                except StopIteration:
                    break

        for output_message in self.finish():
            subtask.send((self, output_message))

    @staticmethod
    def get_parser(parser):
        """Return `argparse` parser with args for `process` methods.
        """
        return parser

    def filter_propagation(self, source, input_message):
        """Return True for messages that must be propagated.
        """
        return True

    def filter_processing(self, source, input_message):
        """Return True for messages that must be processed in current task
        """
        # source implement any allowed protocol
        if source.implement & self.sources:
            return True
        # source name in allowed sources
        if source.name in self.sources:
            return True
        return False

    def process(self):
        """Main task logic.
        Get messages and return some messages for each.

        Get message:
        ```
        source, message = yield
        ```

        Return new message:
        ```
        yield message
        ```
        """
        yield

    def finish(self):
        """Logic after parent task finishing. Must return any iterator.
        """
        return ()

    def update_args(self, args):
        """Update `args` dict from user input
        """
        args, _argv = self.parser.parse_known_args(args)
        return self.args.update(dict(args._get_kwargs()))

    def describe(self):
        """Return task text description.
        """
        descr = self.parser.format_help()
        defaults = []
        for k, v in self.args.items():
            if v is None:
                defaults.append('  {} has no value'.format(k))
            else:
                defaults.append('  {} = {}'.format(k, v))
        if not defaults:
            return descr
        defaults = '\n'.join(sorted(defaults))
        return descr + '\nCurrent values:\n' + defaults

    def add(self, task):
        """Add new subtask into command's subtasks list
        """
        self.subtasks.append(task)

    def __repr__(self):
        return 'Task({})'.format(self.name)
