import abc
import collections
import humanfriendly
import itertools
import os
import re
import subprocess
import sys
import time

from admiral import support


def get_jobmanager(scheduler):
    if scheduler.lower() == "slurm":
        from admiral import slurm
        return slurm.SLURM_Jobmanager

    raise support.JobmanagerException(
        "Unknown scheduler: '{}'; currently only slurm is supported".format(scheduler))


    
class Jobmanager(object):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, batch_dir=None, log_dir=None):
        self.batch_dir = support.path_with_default(batch_dir)
        self.log_dir = support.path_with_default(log_dir)

    def make_job(self, command, **kwdargs):
        return self.job_class()(self, command, **kwdargs)

    @support.abstractstatic
    def job_class():
        pass


        
class Job(object):
    __metaclass__ = abc.ABCMeta
        
    def __init__(self, jobmanager, command, job_name="job", cpus=1, 
                 mem="4g", time="1h", queue=None, array=None, depends=None, dependency_type="afterok"):
        
        self.jobmanager = jobmanager
        
        self.command = command
        self.array = array
        self.job_name = job_name
        
        self.queue = queue

        self.cpus = cpus
        self.mem = humanfriendly.parse_size(mem) # memory in bytes
        self.time = humanfriendly.parse_timespan(time) # time in seconds (float)

        self.depends = depends
        self.dependency_type = dependency_type
        
        self.job_id = None
        self._status = None

        
    @staticmethod
    def done_codes():
        return set(["completed", "canceled", "failed"])

    
    def run(self, tries=1, wait=30):
        batch_script, self.log_path = self.generate_batch_script()
        self.batch_path = self._write_batch_script(batch_script)

        cur_wait = 1
        
        for i in range(tries):
            try:
                self.job_id = self.submit_batch(
                    self.batch_path, self.job_name, self.array, self.depends, self.dependency_type)
                break
            except Exception as e:
                error_message = "Error submitting job: '{}'".format(e)
                if i < tries-1:
                    print(error_message + " ... trying again (try {}/{})".format(
                        i+1, tries))
                else:
                    raise support.JobSubmissionException(error_message)

            time.sleep(cur_wait)
            cur_wait = min(cur_wait*2, wait)


    def ready(self):
        if self._status in self.done_codes():
            return True

        self._status = self.status()
        if self._status in self.done_codes():
            return True

        return False

    @abc.abstractmethod
    def status(self):
        self._status = self.status()
        return self._status

        
    @support.abstractstatic
    def template(self):
        pass

    def extras(self):
        return ""
        
    def generate_batch_script(self):
        log_path = self._unique_path(self.jobmanager.log_dir)
        mem_mb = int(self.mem / 2**20)

        days, remainder = divmod(self.time, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        args = {
            "queue": self.queue,
            "job_name": self.job_name,
            "log_path": log_path,
            "cpus": self.cpus,
            "mem_mb": mem_mb,
            "days": int(days),
            "hours": int(hours),
            "minutes": int(minutes),
            "seconds": int(seconds),
            "command": self.command,
            "extras": self.extras()
            }

        batch_script = self.template().format(**args)

        return batch_script, log_path
        
    def _unique_path(self, base):
        for i in range(1000):
            if i == 0:
                unique_label = ""
            else:
                unique_label = ".{}".format(i)
                
            batch_path = os.path.join(base, self.job_name+unique_label+".batch")
            if not os.path.exists(batch_path):
                return batch_path

        raise support.JobmanagerException("please use a unique job_name!")

    def _write_batch_script(self, batch_script):
        batch_path = self._unique_path(self.jobmanager.batch_dir)

        assert not os.path.exists(batch_path)
        
        with open(batch_path, "w") as batch_file:
            batch_file.write(batch_script)

        return batch_path


        
def wait_for_jobs(jobs, timeout=-1, wait=0.5, tries=10, progress=False):
    t0 = time.time()

    jobmanagers = set(job.jobmanager for job in jobs)
    if len(jobmanagers) > 1:
        raise support.JobmanagerException("Need to all be from the same jobmanager!")
    jobmanager = jobmanagers.pop()
    
    tried = 0
    
    while (timeout == -1) or (time.time() - t0) < timeout:
        try:
            statuses = collections.Counter(
                job.status() for job in jobs)
            
            if set(statuses).issubset(Job.done_codes()):
                break

            if progress:
                sys.stderr.write("\r{} {}".format(time.time()-t0, statuses))

        except subprocess.CalledProcessError:
            if tried < tries:
                tried += 1
                continue

        tried = 0
        time.sleep(wait)

    if progress:
        sys.stderr.write("\n")
        
    statuses = [job.status() for job in jobs]
    success = set(statuses) == set(["completed"])

    return success



