"""Launch a parallel job

If run on a known machine, will generate a run script and submit a job for
execution. By default just uses mpirun
"""

__all__ = ['launch']

from boutpy.boututils import shell, determineNumberOfCPUs


def launch(command, runcmd="mpirun -np", nproc=None, output=None,
           pipe=False, verbose=False):
    """Launch parallel MPI jobs

    Parameters
    ----------
    command : str
        The command to run.
    runcmd : str, optional, default: "mpirun -p"
        Command for running parallel job.
    nproc : int, optional
        Number of processors used for parallel job.
        Use all cpus on this machine.
    output : str, optional
        Optional name of file for output.
    pipe : bool, optional, default: False
        Redirect the ``stdout`` as part of return if ``pipe=True``.
    verbose : bool, optional, default: False
        output more information.

    Returns
    -------
    tuple(status, output)
    status : int
        Exit code of shell command
    output : str
        ``stdout`` if ``pipe=True``, otherwise ``None`` by default.

    """

    if nproc is None:
        # Determine number of CPUs on this machine
        nproc = determineNumberOfCPUs()

    cmd = runcmd + " " + str(nproc) + " " + command

    if output is not None:
        cmd = cmd + " > " + output

    if verbose:
        print cmd

    return shell(cmd, pipe=pipe)
