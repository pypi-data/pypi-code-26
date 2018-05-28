import inspect
import sys
from os import path

from pycallgraph import PyCallGraph, Config, GlobbingFilter
from pycallgraph.output import GraphvizOutput

call_graph_config = Config()
call_graph_config.trace_filter = GlobbingFilter(exclude=[
    'pycallgraph.*',
], )


def generate_call_graph(graph_path, func, *args, **kwargs):
    """Generates Call Graph for the called function"""
    caller_func = "test_" + func.__name__
    if len(args) > 1:
        caller_func += "_" + "_".join(args[1:])
    with PyCallGraph(output=GraphvizOutput(output_file=path.join(graph_path, "{0}.png".format(caller_func)),
                                           output_format="png"), config=call_graph_config):
        return func(*args, **kwargs)
