# pylint:disable=W,C,R

from sys import argv, exit as sys_exit


class Script(object):

    @staticmethod
    def load_args(args=None):
        if args is None:
            args = argv[1:]
        return args

    def parse_args(self, process_args=None, *args, **kwargs):
        """"""

    def construct_output(self, *args, **kwargs):
        """"""

    def format_output(self, *args, **kwargs):
        """"""

    def dump_output(self, *args, **kwargs):
        """"""

    def loop_callback(self, *args, **kwargs):
        """"""

    @classmethod
    def bootstrap(cls, process_args=None, *args, **kwargs):
        script = cls(*args, **kwargs)
        loaded_args = script.load_args(process_args)
        script.parse_args(process_args=loaded_args, *args, **kwargs)
        script.loop_callback(*args, **kwargs)
        script.construct_output(*args, **kwargs)
        script.format_output(*args, **kwargs)
        script.dump_output(*args, **kwargs)
