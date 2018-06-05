"""Get environment variable. """

__all__ = ['getmpirun']

from os import getenv


def getmpirun(default="mpirun -np"):
    """Return environment variable named MPIRUN

    Parameters
    ----------
    default: str, optional
        if the environment variable ``MPIRUN`` does not exist,
        then return default value.

    """

    MPIRUN = getenv("MPIRUN")

    if MPIRUN is None:
        MPIRUN = default
        print "getmpirun: using the default ", default

    return MPIRUN
