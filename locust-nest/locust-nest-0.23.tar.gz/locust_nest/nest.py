import glob
import inspect
import json
import logging
import os
import random
import sys

from locust import HttpLocust, TaskSet, task

logger = logging.getLogger(__name__)


def is_taskset(tup, ignore_prefix='_'):
    """Takes (name, object) tuple, returns True if it's a
    public TaskSet subclass."""
    name, item = tup
    return bool(
        inspect.isclass(item) and
        issubclass(item, TaskSet) and
        hasattr(item, "tasks") and
        not name.startswith(ignore_prefix) and
        name != 'TaskSet'
    )


def load_taskset_file(path, ignore_class_prefix='_'):
    """Import given taskfile path and return (docstring, callables).
    Specifically, the taskfile's ``__doc__`` attribute (a string) and a
    dictionary of ``{'name': callable}`` containing all callables which pass
    the "is a TaskSet" test.

    Arguments:
        path {string} -- path to file to search for TaskSets.

    Returns:
        dict -- {__doc__:class callable, ...} for each TaskSet class that
                does not start with *ignore_class_prefix*.

    """
    # Get directory and taskfile name
    directory, taskfile = os.path.split(path)
    # If the directory isn't in the PYTHONPATH, add it so our import will work
    added_to_path = False
    index = None
    if directory not in sys.path:
        sys.path.insert(0, directory)
        added_to_path = True
    # If the directory IS in the PYTHONPATH, move it to the front temporarily,
    # otherwise other taskfiles -- like Locusts's own -- may scoop the intended
    # one.
    else:
        i = sys.path.index(directory)
        if i != 0:
            # Store index for later restoration
            index = i
            # Add to front, then remove from original position
            sys.path.insert(0, directory)
            del sys.path[i + 1]

    # Perform the import (trimming off the .py)
    imported = __import__(os.path.splitext(taskfile)[0])
    # Remove directory from path if we added it ourselves (just to be neat)
    if added_to_path:
        del sys.path[0]

    # Put back in original index if we moved it
    if index is not None:
        sys.path.insert(index + 1, directory)
        del sys.path[0]

    # Return our two-tuple
    tasksets = dict(filter(lambda x: is_taskset(x, ignore_class_prefix),
                    vars(imported).items()))
    return tasksets


def load_taskset_dir(dir_path='tasksets/', ignore_file_prefix='_'):
    """Searches the directory at *dir_path* and subdirectories for all TaskSet
    sub-classes not starting with *ignore_prefix*, finds and imports all
    tasksets and returns dictionary with name and class callable.

    Arguments:
        dir_path {string} -- path to the directory to import TaskSet classes.
        ignore_file_prefix {string} -- Ignore all files starting with prefix.

    Returns: dict -- {__doc__:class callable} for each *.py file in *dir_path*.

    """
    tasksets = {}
    filepaths = (glob.glob('{}**/*.py'.format(dir_path)) +
                 glob.glob('{}/*.py'.format(dir_path)))
    if not filepaths:
        err = 'No .py files found in "{}"'.format(filepaths)
        logger.warning(err)
        return None

    for filepath in filepaths:
        _, filename = os.path.split(filepath)
        if not filename.startswith(ignore_file_prefix):
            logger.info('Checking {} for TaskSets'.format(filepath))
            t2 = load_taskset_file(filepath)
            tasksets.update(t2)
    return tasksets


def collect_tasksets(dir_path='tasksets/', config_file='config.json'):
    """Load tasksets into a dictionary format used by TaskSets to specify
    tasks and their weights. Adds the stop() method to the tasks of all
    TaskSets imported in this way.

    Returns:
        dict -- {class callable : weight, ... } 
                OR empty dict if no TaskSets are found.

    """

    config = {}
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            try:
                config = json.load(f)
            except ValueError:
                # Config format invalid
                logging.warning(
                    'Config file ({}) format invalid.'.format(config_file)
                )
                pass
    else:
        logging.info('No config file found, will use defaults.')
    tasksets = load_taskset_dir(dir_path)
    if not tasksets:
        return {}
    nest_tasks = {}
    weights = config.get('models', None)
    for key, callee in tasksets.items():
        try:
            weight = weights[key]
        except TypeError:
            msg = """No weight given for {} TaskSet in config,
                     using default from TaskSet.""".format(key)
            logger.info(msg)
            try:
                weight = callee.weight
            except AttributeError:
                msg = """No default weight given for {} TaskSet in TaskSet
                         definition {}.weight, using 1.""".format(key, key)
                logger.info(msg)
                weight = 1
        # If weight is zero, don't add taskset

        def stop(self):
            self.interrupt()

        if weight:
            callee.tasks.append(stop)
            nest_tasks[callee] = weight
    logger.info("Found following tasksets and weights: {}".format(nest_tasks))
    return nest_tasks
