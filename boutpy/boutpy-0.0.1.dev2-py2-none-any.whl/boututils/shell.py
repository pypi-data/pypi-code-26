"""Run a shell command. """
# from __future__ import print_function

__all__ = ['shell', 'jobinfo']

try:
    # Python 2.4 onwards
    from subprocess import call, Popen, STDOUT, PIPE
    # subprocess.check_output, subprocess.check_call
    lib = "call"
except:
    # Use os.system (depreciated)
    from os import popen4, system
    lib = "system"

from boutpy.boututils.compare_inp import parser_config


def shell(command, pipe=False):
    """Return the status and output of a shell command.

    Parameters
    ----------
    command : str
        Shell command
    pipe : bool, optional, default: False.
        Redirect the `stdout` as part of return if ``pipe=True``.

    Returns
    -------
    status : int
        Exit code of shell command
    output : str, None
        ``stdout`` if ``pipe=True``, otherwise ``None`` by default.

    """
    output = None
    status = 0
    if lib == "system":
        if pipe:
            handle = popen4(command)
            output = handle[1].read()
        else:
            status = system(command)
    else:
        if pipe:
            child = Popen(command, stderr=STDOUT, stdout=PIPE, shell=True)
            output = child.stdout.read()
            status = child.returncode
        else:
            status = call(command, shell=True)

    return status, output


def jobinfo(jobid):
    """Return a dict containing all information of the slurm job.

    Parameters
    ----------
    jobid : str, int
        Slurm jobid.

    Returns
    -------
    jobinfo : dict, None
        An dict cantains all information of the slurm job ``jobid``.
        "None" if failed.

    """

    status, output = shell('scontrol show jobid {}'.format(jobid), pipe=True)

    # pre-conditioner, speed up checking info
    if isinstance(jobid, str) and (not jobid.isdigit()):
        raise ValueError('Invalid job id specified!')

    try:
        jobinfo = parser_config('\n'.join(output.split()))
    except:
        jobinfo = None
        raise ValueError('Invalid job id specified!')

    return jobinfo
