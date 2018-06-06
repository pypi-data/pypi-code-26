"""An python api for the endpoints in job_status."""
import logging

import requests

from .utils import DotMapJob, DotMapTask

logger = logging.getLogger(__name__)


# ##############################################################################
# ############################ CREATE ##########################################
# ##############################################################################
def create_job(uuid=None, name=None, payload_text=None, status=None):
    """API for /create_job endpoint. Creates a new job and returns a job object.

    Args:
        uuid (str): Unique custom ID.
        name (str): Name.
        payload_text (str): Text payload.
        status (str): Status.

    Returns:
        DotMap (job): A DotMap object that contains the details job and its tasks.
    """
    logger.debug('web_api/create_job: name: {}, uuid: {}'.format(name, uuid))
    response = requests.post(url="http://localhost:27131/job_status/create_job",
                             data={
                                 'uuid': uuid,
                                 'name': name,
                                 'payload_text': payload_text,
                                 'status': status,
                             })
    job_json = response.json()
    job = DotMapJob(job_json)
    return job


def create_task(job_id, uuid=None, name=None, payload_text=None, status=None):
    """API for /create_task endpoint. Creates a new task and returns a task object.

    Args:
        job_id (int): The ID under which to create a task.
        uuid (str): Unique custom ID.
        name (str): Name.
        payload_text (str): Text payload.
        status (str): Status.

    Returns:
        DotMap (Task): A DotMap object that contains the details of the task.
    """
    logger.debug('web_apli/create_task: job_id: {}'.format(job_id))
    response = requests.post(url="http://localhost:27131/job_status/create_task",
                             data={
                                 'job_id': job_id,
                                 'uuid': uuid,
                                 'name': name,
                                 'payload_text': payload_text,
                                 'status': status,
                             })
    task_json = response.json()
    task = DotMapTask(task_json)
    return task


# ##############################################################################
# ############################# UPDATE #########################################
# ##############################################################################
def update_job(job_id, uuid=None, name=None, payload_text=None, status=None):
    """API for /update_job endpoint. Updates job.

    Args:
        job_id (int): The id of the job which need to be updated.
        uuid (str): Unique custom ID.
        name (str): Name.
        payload_text (str): Text payload.
        status (str): Status.

    Returns:
        DotMap (Task): A DotMap object that contains the details of the job.
    """
    logger.debug('web_apli/update_job: job_id: {}, uuid: {}, name: {}, status: {}, payload_text: {}'
                 .format(job_id, uuid, name, status, payload_text))
    response = requests.post(url="http://localhost:27131/job_status/update_job",
                             data={
                                 'job_id': job_id,
                                 'uuid': uuid,
                                 'name': name,
                                 'payload_text': payload_text,
                                 'status': status,
                             })
    job_json = response.json()
    job = DotMapJob(job_json)
    return job


def update_task(task_id, uuid=None, name=None, payload_text=None, status=None, update_parent_job=None):
    """API for /update_task endpoint. Updates task.

    Args:
        task_id (int): The id of the task which need to be updated.
        uuid (str): Unique custom ID.
        name (str): Name.
        payload_text (str): Text payload.
        status (str): Status.

    Returns:
        DotMap (Task): A DotMap object that contains the details of the task.
    """
    logger.debug('web_api/update_task: task_id: {}, uuid: {}, name: {}, status: {}, payload_text: {}, update_parent_job: {}'
                 .format(task_id, uuid, name, status, payload_text, update_parent_job))
    response = requests.post(url="http://localhost:27131/job_status/update_task",
                             data={
                                 'task_id': task_id,
                                 'uuid': uuid,
                                 'name': name,
                                 'payload_text': payload_text,
                                 'status': status,
                                 'update_parent_job': update_parent_job
                             })
    task_json = response.json()
    task = DotMapTask(task_json)
    return task


# ##############################################################################
# ############################# READ ###########################################
# ##############################################################################
def read_job(job_id):
    """API for /read_job endpoint. Read job.

    Args:
        job_id (int): The id of the job to read.

    Returns:
        DotMap (job): A DotMap object that contains the details job and its tasks.
    """
    logger.debug('web_api/read_job: job_id: {}'.format(job_id))
    response = requests.get(url="http://localhost:27131/job_status/read_job", params={'job_id': job_id})
    job_dict = response.json()
    job = DotMapJob(job_dict)
    return job


def read_all_jobs():
    """API for /read_job endpoint. Read job.

    Returns:
        DotMap (list of jobs): A DotMap object that contains the details job and its tasks.
    """
    logger.debug('web_api/read_all_jobs')
    response = requests.get(url="http://localhost:27131/job_status/read_all_jobs")
    jobs = response.json()
    jobs = [DotMapJob(job_dict) for job_dict in jobs]
    return jobs


def read_task(task_id):
    """API for /read_task endpoint. Read task.

    Args:
        task_id (int): The id of the task to read.

    Returns:
        DotMap (Task): A DotMap object that contains the details of the task.
    """
    logger.debug('web_api/read_task: task_id: {}'.format(task_id))
    response = requests.get(url="http://localhost:27131/job_status/read_task",
                            params={'task_id': task_id})
    task_dict = response.json()
    task = DotMapTask(task_dict)
    return task


def read_task_from_uuid(task_uuid):
    """API for /read_task endpoint. Read task.

    Args:
        task_uuid (str): The uuid of the task to read.

    Returns:
        DotMap (Task): A DotMap object that contains the details of the task.
    """
    logger.debug('web_api/read_task_from_uuid: task_uuid: {}'.format(task_uuid))
    response = requests.get(url="http://localhost:27131/job_status/read_task_from_uuid",
                            params={'task_uuid': task_uuid})
    task_dict = response.json()
    task = DotMapTask(task_dict)
    return task


if __name__ == "__main__":
    job = create_job()
    print(job.as_json())

    task = create_task(job_id=job.id)
    print(task.as_json())

    task = update_task(task_id=task.id, status='NOT PENDING')
    print(task.as_json())

    old_job = read_job(job_id=job.id)
    print(old_job.as_json())

    old_task = read_task(task_id=task.id)
    print(old_task.as_json())
