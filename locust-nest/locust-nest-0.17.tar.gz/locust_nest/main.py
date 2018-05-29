from . import make_config, save_config, collect_tasksets
from locust import TaskSet, HttpLocust, run_locust, parse_options
import logging
import sys
import os

from optparse import (OptionParser, BadOptionError, AmbiguousOptionError)

sys.path.insert(0, os.getcwd())

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


class PassThroughOptionParser(OptionParser):
    """
    An unknown option pass-through implementation of OptionParser.

    When unknown arguments are encountered, bundle with largs and try again,
    until rargs is depleted.

    sys.exit(status) will still be called if a known argument is passed
    incorrectly (e.g. missing arguments or bad argument types, etc.)        
    """

    def _process_args(self, largs, rargs, values):
        while rargs:
            try:
                OptionParser._process_args(self, largs, rargs, values)
            except (BadOptionError, AmbiguousOptionError), e:
                largs.append(e.opt_str)


def create_parser():
    """Create parser object used for defining all options for Locust.

    Returns:
        OptionParser: OptionParser object used in *parse_options*.
    """

    # Initialize
    parser = PassThroughOptionParser(usage="nest [options] Locust options")

    parser.add_option(
        '--configure',
        action='store_true',
        dest='configure',
        default=False,
        help="Generate config file using helper."
    )

    parser.add_option(
        '--config_file',
        action='store',
        dest='config_file',
        default='config.json',
        help="Specify config file location."
    )

    parser.add_option(
        '-T', '--taskset_dir',
        action='store',
        dest='taskset_dir',
        default='tasksets/',
        help="Specify directory containing TaskSets."
    )

    # Version number (optparse gives you:version but we have to do it
    # ourselves to get -V too. sigh)
    parser.add_option(
        '-V', '--version',
        action='store_true',
        dest='show_version',
        default=False,
        help="show program's version number and exit"
    )
    return parser


def parse_nest_options(args=sys.argv):
    """
    Handle command-line options with optparse.OptionParser.

    Return list of arguments, largely for use in `parse_arguments`.
    """
    parser = create_parser()
    # Return tuple of the output from parse_args (opt obj, args)
    opts, args = parser.parse_args(args)
    return opts, args


def main(sys_args=None):
    nest_opts, nest_args = parse_nest_options(sys_args[1:])
    taskset_dir = nest_opts.taskset_dir
    if nest_opts.configure:
        save_config(make_config(taskset_dir), nest_opts.config_file)

    nest_tasks = collect_tasksets(dir_path=taskset_dir)
    if not nest_tasks:
        logger.warning('No tasks found in {}'.format(taskset_dir))

    class NestTaskSet(TaskSet):
        """TaskSet containing all the sub-tasksets contained
        in the specified directory.

        Arguments:
            TaskSet {class} -- TaskSet class from Locust.

        """
        tasks = nest_tasks

    class NestLocust(HttpLocust):
        """HttpLocust using the NestTaskSet.

        Arguments:
            HttpLocust {class} -- HttpLocust from Locust.

        """
        task_set = NestTaskSet

    _, locust_opts, locust_args = parse_options(nest_args)
    locust_opts.locust_classes = [NestLocust]
    run_locust(locust_opts, locust_args)


if __name__ == "__main__":
    main()
