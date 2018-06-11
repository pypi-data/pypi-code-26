import itertools
import re
import subprocess

from admiral.jobmanagers import Job, Jobmanager
from admiral.support import JobmanagerException, JobSubmissionException


SLURM_TEMPLATE = \
"""#!/bin/sh
#SBATCH -p {queue}
#SBATCH -J {job_name}
#SBATCH -o {log_path}_%A_%a.out
#SBATCH -e {log_path}_%A_%a.err
#SBATCH --cpus-per-task={cpus}
#SBATCH --mem={mem_mb}
#SBATCH -t {days}-{hours}:{minutes}:{seconds}
{extras}

{command}
"""


class SLURM_Jobmanager(Jobmanager):
    @staticmethod
    def job_class():
        return SLURM_Job

        
        
class SLURM_Job(Job):
    @staticmethod
    def template():
        return SLURM_TEMPLATE

    @staticmethod
    def submit_batch(batch_path, job_name, array=None, depends=None, dependency_type="afterok", verbose=True):
        array_command = ""
        if array is not None:
            array_command = "--array={} ".format(array)

        extras = ""
        if depends:
            extras += "--dependency={}:{}".format(dependency_type, ":".join(map(str, depends))) + " "

        command = "sbatch {}{}{}".format(extras, array_command, batch_path)
        if verbose:
            print("Launching command:'", command, "'")

        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = process.wait()
        if result != 0:
            error = "Error submitting job '{}'\n".format(job_name)
            error = error + " command: '{}'".format(command) + "\n stdout: '{}'\nstderr: '{}'".format(
                process.stdout.read(), process.stderr.read())
            raise JobSubmissionException(error)

        output = process.stdout.read().decode()
        job_id_match = re.search(r"Submitted batch job (\d+)", output.strip())
        if job_id_match is None:
            raise JobSubmissionException(
                "Error parsing job id from output '{}'".format(output))

        return job_id_match.group(1)


    def status(self):
        if self.job_id is None:
            raise JobmanagerException("Must submit job first!")

        if self._status in self.done_codes():
            return self._status

        sacct_format = "JobID%50,JobName,State,ExitCode"

        # hack because apparently -j option looks back infinitely into the past
        import datetime
        long_ago = (datetime.date.today() - datetime.timedelta(days=14)).strftime("%Y-%m-%d")
        status_command = "sacct --noheader -o {} -j {} --starttime {}".format(
            sacct_format, self.job_id, long_ago)
        
        result = subprocess.check_output(status_command, shell=True)

        status = None
        progress = {}
        
        for line in result.splitlines():
            line = line.decode()
            job_id, job_name, state, exit_code = line.strip().split()

            state = state.split()[0].replace("+","")
            cur_status = None
            if state in ["PENDING", "REQUEUED"]:
                cur_status  = "pending"
            elif state == "RUNNING":
                cur_status = "running"
            elif state == "COMPLETED":
                cur_status = "completed"
            elif state == "CANCELLED":
                cur_status = "canceled"
            elif state == "FAILED":
                cur_status = "failed"

            
            if self.array is not None:
                part, part_label = self._match_job_id(job_id)
                if part in ["step", "remainder"]:
                    progress[part_label] = cur_status
            else:
                status = cur_status
            
        if self.array is not None:
            statuses = set(progress.values())
            if "running" in statuses:
                status = "running"
            elif "pending" in statuses:
                status = "pending"
            elif "failed" in statuses:
                status = "failed"
            elif "canceled" in statuses:
                status = "canceled"
            elif "completed" in statuses:
                status = "completed"

        if status is None:
            status = "unknown"
            
        self._status = status
        
        return status


    def _array_job_ids(self):
        assert self.array is not None

        start, end = self.array.split("-")
        start = int(start)
        end = int(end)

        job_ids = ["{}_{}".format(self.job_id, i) for i in range(start, end+1)]

        return job_ids

    def _match_job_id(self, tomatch):
        step_re = "{}_(\d+)$".format(self.job_id)
        remainder_re = "{}_\[(.+)\]$".format(self.job_id)

        step = re.match(step_re, tomatch)
        if step is not None:
            step_id = int(step.group(1))
            return "step", step_id

        remainder = re.match(remainder_re, tomatch)
        if remainder is not None:
            remainder = remainder.group(1)
            return "remainder", remainder

        return ("unknown",-1)
