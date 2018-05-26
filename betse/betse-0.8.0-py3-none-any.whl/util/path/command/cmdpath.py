#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright 2014-2018 by Alexis Pietak & Cecil Curry.
# See "LICENSE" for further details.

'''
Low-level **pathable** (i.e., commands reseding in the current ``${PATH}`` and
hence executable by specifying merely their basename rather than either relative
or absolute path) facilities.
'''

# ....................{ IMPORTS                            }....................
import shutil
from betse.exceptions import BetseCommandException
from betse.util.type.types import type_check, SequenceTypes, StrOrNoneTypes

# ....................{ TESTERS                            }....................
@type_check
def is_pathable(command_basename: str) -> bool:
    '''
    ``True`` only if an external command with the passed basename exists (i.e.,
    corresponds to an executable file in the current ``${PATH}``).

    Caveats
    ----------
    For safety, avoid appending the passed basename by a platform-specific
    filetype -- especially, a Windows-specific filetype. On that platform, this
    function iteratively appends this basename by each filetype associated with
    executable files listed by the ``%PATHEXT%`` environment variable (e.g.,
    ``.bat``, ``.cmd``, ``.com``, ``.exe``) until the resulting basename is that
    of an executable file in the current ``%PATH%``.

    Parameters
    ----------
    command_basename : str
        Basename of the command to be searched for.

    Raises
    ----------
    BetsePathException
        If the passed string is *not* a basename (i.e., contains one or more
        directory separators).

    See Also
    ----------
    :func:`betse.util.path.command.commands.is_command`
        A more general-purpose and hence generally useful tester returning
        whether a command with the passed path (regardless of whether that
        path is a basename) exists.
    '''

    # Avoid circular import dependencies.
    from betse.util.path import pathnames

    # If this string is *NOT* a pure basename, fail.
    pathnames.die_unless_basename(command_basename)

    # Return whether this command exists or not.
    return shutil.which(command_basename) is not None

# ....................{ GETTERS                            }....................
@type_check
def get_filename(command_basename: str) -> str:
    '''
    Absolute path of the command in the current ``${PATH}`` with the passed
    basename if found *or* raise an exception otherwise.

    Parameters
    ----------
    command_basename : str
        Basename of the command to return the absolute path of.

    Returns
    ----------
    str
        Absolute path of this command.

    Raises
    ----------
    BetseCommandException
        If no such command is found.
    '''

    # Absolute path of this command if found or "None" otherwise.
    command_filename = get_filename_or_none(command_basename)

    # If this command is *NOT* found, raise an exception.
    if command_filename is None:
        raise BetseCommandException(
            'Command "{}" not found.'.format(command_basename))

    # Return this path.
    return command_filename


@type_check
def get_filename_or_none(command_basename: str) -> StrOrNoneTypes:
    '''
    Absolute path of the command in the current ``${PATH}`` with the passed
    basename if found *or* ``None`` otherwise.

    Parameters
    ----------
    command_basename : str
        Basename of the command to return the absolute path of.

    Returns
    ----------
    StrOrNoneTypes
        Either;
        * Absolute path of this command if found.
        * ``None`` otherwise.
    '''

    # Avoid circular import dependencies.
    from betse.util.path import pathnames

    # If this string is *NOT* a pure basename, fail.
    pathnames.die_unless_basename(command_basename)

    # Return the absolute path of this command if found or "None" otherwise.
    return shutil.which(command_basename)

# ....................{ GETTERS ~ first                    }....................
@type_check
def get_first_basename(
    command_basenames: SequenceTypes, exception_message: str = None) -> str:
    '''
    First pathable string in the passed list (i.e., the first string that is the
    basename of a command in the current ``${PATH}``) if any *or* raise an
    exception otherwise.

    Parameters
    ----------
    command_basenames : SequenceTypes
        List of the basenames of all commands to be iteratively searched for
        (in descending order of preference).
    exception_message : optional[str]
        Optional exception message to be raised if no such string is pathable.
        Defaults to ``None``, in which case an exception message synthesized
        from the passed strings is raised.

    Returns
    ----------
    str
        First pathable string in the passed list.

    Raises
    ----------
    BetseCommandException
        If no passed strings are pathable.
    '''

    # Avoid circular import dependencies.
    from betse.util.type.text import strs

    # Return the first pathable string in this list.
    for command_basename in command_basenames:
        if is_pathable(command_basename):
            return command_basename

    # Else, no such string is pathable. In this case, raise an exception.
    exception_message_suffix = (
        '{} not found in the current ${{PATH}}.'.format(
            strs.join_as_conjunction_double_quoted(*command_basenames)))

    # If a non-empty exception message is passed, suffix this message with this
    # detailed explanation.
    if exception_message:
        exception_message += ' ' + exception_message_suffix
    # Else, default this message to this detailed explanation.
    else:
        exception_message = exception_message_suffix

    # Raise this exception.
    raise BetseCommandException(exception_message)
