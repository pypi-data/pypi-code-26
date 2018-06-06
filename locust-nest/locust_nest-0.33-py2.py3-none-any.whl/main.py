from configure import make_config, save_config, retry_valid_input
from nest import collect_tasksets, collect_locusts
from locust import TaskSet, HttpLocust, run_locust, parse_options
from version import __version__ as version
import logging
import sys
import os

import argparse
sys.path.insert(0, os.getcwd())

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


def create_parser():
    """Create parser object used for defining all options for Locust.

    Returns:
        OptionParser: OptionParser object used in *parse_options*.
    """

    # Initialize
    parser = argparse.ArgumentParser(usage="nest [options] Locust options")

    parser.add_argument(
        '--configure',
        action='store_true',
        dest='configure',
        default=False,
        help="Generate config file using helper."
    )

    parser.add_argument(
        '--config_file',
        action='store',
        dest='config_file',
        default='config.json',
        help="Specify config file location."
    )

    parser.add_argument(
        '-T', '--include-tasksets',
        action='store_true',
        dest='include_tasksets',
        default=False,
        help="Whether or not to include TaskSets."
    )

    parser.add_argument(
        '-d', '--model_dir',
        action='store',
        dest='model_dir',
        default=None,
        help="Specify directory containing TaskSets or Locusts."
    )

    parser.add_argument(
        '-V', '--version',
        action='store_true',
        dest='show_version',
        default=False,
        help="show program's version number and exit"
    )
    return parser


def main(args=None):
    """Load all TaskSets and Locusts from --model_dir according to --config_file.
    --configure option will guide generation of config file before launching.
    Will pass on all standard Locust arguments to run_locust.

    Keyword Arguments:
        args {list} -- Command line arguments (default: {None})
    """

    parser = create_parser()
    nest_opts, nest_args = parser.parse_known_args()
    include_tasksets = nest_opts.include_tasksets

    if nest_opts.show_version:
        print("locust-nest version {}".format(version))
        sys.exit(0)

    model_dir = nest_opts.model_dir
    if model_dir is None:
        model_dir = retry_valid_input(
                prompt='Enter the path of your model directory:',
                title='directory',
                default='models/',
                condition=os.path.exists)

    if nest_opts.configure:
        save_config(make_config(model_dir, include_tasksets), nest_opts.config_file)

    # Locust classes model_dir = nest_opts.model_dir
    locust_classes = collect_locusts(model_dir)

    # Tasksets
    if include_tasksets:
        nest_tasks = collect_tasksets(dir_path=model_dir)
        if not nest_tasks:
            logger.warning('No TaskSets found in {}'.format(model_dir))

        if nest_tasks:
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
                weight = 1
            locust_classes.append(NestLocust)

    _, locust_opts, locust_args = parse_options(nest_args)
    locust_opts.locust_classes = locust_classes
    if not locust_classes:
        print("No classes found for simulation, exiting.")
        sys.exit(1)
    run_locust(locust_opts, locust_args)


if __name__ == "__main__":
    main()
