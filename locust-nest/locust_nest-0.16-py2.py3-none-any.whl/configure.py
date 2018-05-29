from . import load_taskset_dir
import json
import sys
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


def is_int(string):
    """Returns True if int(string) doesn't fail, otherwise false.

    Arguments:
        string {str} -- string to test

    Returns:
        bool -- Can string be converted into an int?

    """
    try:
        int(string)
        return True
    except ValueError:
        return False


# Keep trying user input until condition is met
def retry_valid_input(
        prompt,
        title='',
        default=None,
        condition=lambda x: x is not None,
        transform=lambda x: x):
    """Keep asking user for input until user input satifies *condition* function.

    Arguments:
        prompt {str} -- User prompt text.

    Keyword Arguments:
        title {str} -- Name of this request for information. (default: {''})
        default {Any} -- Default value of user input. Be careful that default
                         passes condition. (default: {None})
        condition {function: a -> bool} --
                Condition returning boolean to signal correct input from user.
                (default: {lambdax:x is not None})
        transform {function: a -> b} --
                Transformation function transforming user data
                before returning it. (default: {lambda x:x})

    Returns:
        b -- Returns result of transform function (defaults to identity)

    """
    if default is not None:
        prompt += ' [{}]'.format(default)
    while True:
        user_input = raw_input(prompt) or default
        # If user_input passes the condition, transform and save the output
        if condition(user_input):
            break
        else:
            print('Invalid {}'.format(title))
    return transform(user_input)


def make_config(dir_path=None, **kwargs):
    """Guide a user through making a config file for Nest.

    Keyword Arguments:
        dir_path {str (path)} -- Folder in which the user's TaskSets reside.
                                 (default: {None})

    Returns:
        dict -- Nest config file.

    """

    # For each TaskSet found using collect tasksets
    # Proportion first / then total amount.
    # If interactive mode, ask for taskset dir (with default)
    if dir_path is None:
        dir_path = retry_valid_input(
                prompt='Enter the path of your taskset directory:',
                title='directory',
                default='tasksets/',
                condition=os.path.exists)
    tasksets = load_taskset_dir(dir_path)

    # Set quantities of various tasks
    quantities = {}
    total = 0

    def default_weight(callee):
        # try:
        return callee.weight

    for name, callee in tasksets.items():
        quantity = kwargs.get(name, None)
        if quantity is None:
            quantity = retry_valid_input(
                    prompt='How many {}s would you like to have?'.format(name),
                    title='quantity',
                    condition=is_int,
                    default=default_weight(callee),
                    transform=int)
        quantities[name] = quantity
        total += quantity
        # for task in callee.tasks:
        # logger.debug(task.func_name)
    # logger.info('Quantities: {}'.format(quantities))
    # logger.info('Total: {}'.format(total))
    config = {
        'models': quantities,
        'total': total
    }
    return config


def save_config(config, config_file=None):
    """Helper to save config dict to user-defined location.

    Arguments:
        config {dict} -- Config file.

    Keyword Arguments:
        config_file {str (path)} --
                Path to config file. If not specified will
                ask the user. (default: {None})

    Returns:
        bool -- Successful or not.
    """

    # Specify file path to save the config file to
    if config_file is None:
        config_file = retry_valid_input(
                prompt='What would you like to name this config?',
                title='config file',
                default='config.json')
    with open(config_file, 'w') as f:
        json.dump(config, f)
    if os.path.exists(config_file):
        return True
    return False
