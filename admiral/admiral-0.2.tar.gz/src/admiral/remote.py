import importlib
import itertools
import os
import sys

try:
    import cPickle as pickle
except ImportError:
    import pickle
    

from admiral import support


class RunRemoteException(Exception):
    pass


class Order:
    def __init__(self, args, kwdargs):
        self.args = args
        self.kwdargs = kwdargs

def _write_orders(job_dir, job_name, fn, orders, overwrite):
    remote = {
        "function": fn,
        "orders": orders
        }

    remote_instructions_path = os.path.join(
        job_dir, "{}.orders".format(job_name))

    if (not overwrite) and os.path.exists(remote_instructions_path):
        raise RunRemoteException("Remote instructions file already exists:"
                                 "'{}'. Use 'overwrite=True' to overwrite this file")

    with open(remote_instructions_path, "wb") as f:
        pickle.dump(remote, f, protocol=-1)

    return remote_instructions_path

    
def run_remote(fn, jobmanager, job_name, args=None, kwdargs=None,
               njobs=None, job_dir=None, overwrite=False, 
               tries=10, wait=30, **jobmanager_kwdargs):
   
    pythonpath = ":".join(sys.path)

    if job_dir is None:
        job_dir = jobmanager.batch_dir

    
    if kwdargs is None:
        kwdargs = [{}]*len(args)
    if args is None:
        args = [[]]*len(kwdargs)
                           
    assert not isinstance(kwdargs, dict)
    assert len(args) == len(kwdargs)
               
    if njobs is None:
        njobs = len(args)
    assert njobs > 0
    
    njobs = min(njobs, len(args))

    remote_instructions_paths = []
    orders = [Order(cur_arg, cur_kwdarg) for (cur_arg, cur_kwdarg) in zip(args, kwdargs)]

    # for i, (cur_args, cur_kwdargs) in enumerate(zip(args, kwdargs)):
    for i, cur_orders in enumerate(support.get_nchunks(orders, njobs)):
        cur_job_name = "{}_{:05d}".format(job_name, i)
        remote_instructions_paths.append(
            _write_orders(job_dir, cur_job_name,
                          fn, cur_orders, overwrite))
    os.putenv("remote_instructions_paths", " ".join(remote_instructions_paths))
    
    command = ["export PYTHONPATH={pythonpath}",
               "remote_instructions_paths=(${{remote_instructions_paths}})",
               "echo ${{remote_instructions_paths[*]}}",
               "{python} {this} ${{remote_instructions_paths[${{SLURM_ARRAY_TASK_ID}}]}}"]
    command = "\n".join(command)

    command = command.format(pythonpath=pythonpath,
                             remote_instructions_paths=remote_instructions_paths,
                             python=sys.executable,
                             this=__file__)

    array_command = "0-{}".format(njobs-1)
        
    job = jobmanager.make_job(command, job_name=job_name, array=array_command,
                              **jobmanager_kwdargs)
    job.run()

    return job


if __name__ == "__main__":
    remote_instructions_path = sys.argv[1]

    remote_instructions = pickle.load(open(remote_instructions_path, "rb"))

    #print ">>>>>>", remote_instructions
    function = remote_instructions["function"]
    orders = remote_instructions["orders"]

    exceptions = []

    for order in orders:
        try:
            function(*order.args, **order.kwdargs)
        except Exception as e:
            exceptions.append(e)

    for e in exceptions:
        raise e
