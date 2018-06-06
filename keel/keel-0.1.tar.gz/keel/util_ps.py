import psutil
import os


# gets all processes by the specific username
def get_proc_by_username(username):
    results = [p.info for p in psutil.process_iter(attrs=['pid', 'name', 'username']) if
               str(username) in p.info['username']]
    return results


def get_all_proc():
    results = [p.info for p in psutil.process_iter(attrs=['pid', 'name', 'username'])]
    return results


# gets all processes which contain the given name
def get_proc_by_name(procname):
    results = [p.info for p in psutil.process_iter(attrs=['pid', 'name', 'username']) if
               str(procname) in p.info['name']]
    return results


# gets all processes in dictionary where each key is the PID. useful for quick lookup of a specific process by its PID
def get_proc_w_key_pid():
    results = {p.pid: p.info for p in psutil.process_iter(attrs=['name', 'username'])}
    return results


# system-wide connections
def get_open_con(kind):
    results = psutil.net_connections(kind=kind)
    return results


# kill by PID. will return value only if there was an error or the pid is the pid of the current running process
def kill_pid(pid):
    if pid == os.getpid():
        raise RuntimeError('I cannot kill myself')
    if pid is None:
        raise TypeError('PID is None')
    if not psutil.pid_exists(pid):
        raise psutil.NoSuchProcess(pid=pid)
    proc = psutil.Process(pid=pid)
    proc.kill()
