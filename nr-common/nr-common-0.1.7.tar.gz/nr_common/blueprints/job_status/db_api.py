"""Database Functions."""
from .models import Job, Task, db


#######################################
# Job Stuff
#######################################
def insert_new_job(uuid=None, name=None, payload_text=None, status='PENDING'):
    """Insert a new job and return it.

    Creates the job attributes if the attributes are NOT None.

    Args:
        uuid (str): Unique custom ID.
        name (str): Name.
        payload_text (str): Text payload.
        status (str): Status.
    """
    # db = get_db()

    job_kwargs = {}
    if uuid is not None:
        job_kwargs['uuid'] = uuid
    if name is not None:
        job_kwargs['name'] = name
    if payload_text is not None:
        job_kwargs['payload_text'] = payload_text
    if status is not None:
        job_kwargs['status'] = status

    new_job = Job(**job_kwargs)
    db.session.add(new_job)
    db.session.commit()
    db.session.flush()
    return new_job


def select_job_all():
    """Select all jobs."""
    # db = get_db()
    all_jobs = db.session.query(Job).all()
    return all_jobs


def select_job_from_id(job_id):
    """Select job from ID."""
    # db = get_db()
    job = (db.session.query(Job)
           .filter_by(id=job_id)
           .first())
    return job


def select_job_uuid(job_uuid):
    """Select job from UUID."""
    # db = get_db()
    job = (db.session.query(Job)
           .filter_by(uuid=job_uuid)
           .first())
    return job


def update_job(job_id, uuid=None, name=None, payload_text=None, status=None):
    """Update job.

    Updates the job attributes if the attributes are NOT None.

    Args:
        job_id (int): The ID under which to create a task.
        uuid (str): Unique custom ID.
        name (str): Name.
        payload_text (str): Text payload.
        status (str): Status.
    """
    # db = get_db()

    # Get job from job_id
    if job_id is None:
        raise AttributeError("job_id cannot be None")

    job = select_job_from_id(job_id)

    # Update job
    if uuid is not None:
        job.uuid = uuid
    if name is not None:
        job.name = name
    if payload_text is not None:
        job.payload_text = payload_text
    if status is not None:
        job.status = status

    db.session.add(job)
    db.session.commit()
    db.session.flush()
    return job


#######################################
# Task Stuff
#######################################
def insert_new_task(job_id, uuid=None, name=None, payload_text=None, status='PENDING'):
    """Insert a new task and return it.

    Creates the task attributes if the attributes are NOT None.

    Args:
        uuid (str): Unique custom ID.
        name (str): Name.
        payload_text (str): Text payload.
        status (str): Status.
    """
    # db = get_db()

    task_kwargs = {'job_id': job_id}

    if uuid is not None:
        task_kwargs['uuid'] = uuid
    if name is not None:
        task_kwargs['name'] = name
    if payload_text is not None:
        task_kwargs['payload_text'] = payload_text
    if status is not None:
        task_kwargs['status'] = status

    new_task = Task(**task_kwargs)
    db.session.add(new_task)
    db.session.commit()
    db.session.flush()
    return new_task


def select_task_from_id(task_id):
    """Select task from id."""
    # db = get_db()
    task = (db.session.query(Task)
            .filter_by(id=task_id)
            .first())
    return task


def select_task_from_uuid(task_uuid):
    """Select task from UUID."""
    # db = get_db()
    task = (db.session.query(Task)
            .filter_by(uuid=task_uuid)
            .first())
    return task


def update_task(task_id, uuid=None, name=None, payload_text=None, status=None, update_parent_job=None):
    """Update task.

    Updates the task attributes if the attributes are NOT None.

    Args:
        task_id (int): The ID under which to create a task.
        uuid (str): Unique custom ID.
        name (str): Name.
        payload_text (str): Text payload.
        status (str): Status.
    """
    # db = get_db()

    # Get task from task_id
    if task_id is None:
        raise AttributeError("task_id cannot be None")

    task = select_task_from_id(task_id)

    # Update task
    if uuid is not None:
        task.uuid = uuid
    if name is not None:
        task.name = name
    if payload_text is not None:
        task.payload_text = payload_text
    if status is not None:
        task.status = status

    db.session.add(task)
    db.session.commit()
    db.session.flush()

    if update_parent_job == "on_first_task":
        job = select_job_from_id(task.job_id)
        # Check if this task is the first task of the job.
        if job.tasks[0].id == task.id:
            update_job(job.id, status=task.status)
    elif update_parent_job == "on_last_task":
        job = select_job_from_id(task.job_id)
        # Check if this task is the last task of the job.
        if job.tasks[-1].id == task.id:
            update_job(job.id, status=task.status)
    elif update_parent_job == "on_this_task":
        job = select_job_from_id(task.job_id)
        update_job(job.id, status=task.status)
    elif not update_parent_job:
        pass  # Don't update in this case.
    else:
        raise ValueError("update_parent_job must be 'on_first_task', 'on_last_task', 'on_this_task' or Null, not {}."
                         .format(update_parent_job))

    return task
