"""."""
import logging

from flask import Blueprint, jsonify, render_template, request

from . import db_api, web_api

logger = logging.getLogger(__name__)

job_status_handler = Blueprint(name='job_status',
                               import_name=__name__,
                               template_folder='templates',
                               static_folder='static')


# ##############################################################################
# ############################ PAGES ###########################################
# ##############################################################################
@job_status_handler.route('/', methods=['GET'])
def index():
    """Index."""
    return render_template('js_index.html')


@job_status_handler.route('/status/<page_id>', methods=['GET', 'POST'])
def status(page_id):
    """Render draw status page."""
    def get_is_reload(jobs):
        for job in jobs:
            if job.status != 'SUCCESS':
                return True
        # If all statuses are SUCCESS, then don't reload anymore.
        return False

    if page_id == "all":
        jobs = web_api.read_all_jobs()
        is_reload = str(get_is_reload(jobs))
        return render_template('js_status.html', jobs=jobs, page_id='all', is_reload=is_reload)
    else:
        job = web_api.read_job(job_id=page_id)
        jobs = [job]
        is_reload = str(get_is_reload(jobs))
        return render_template('js_status.html', jobs=jobs, page_id=page_id, is_reload=is_reload)


# ##############################################################################
# ############################ CREATE ##########################################
# ##############################################################################


@job_status_handler.route('/create_job', methods=['POST'])
def create_job():
    """Create new task."""
    name = request.form.get('name', None)
    uuid = request.form.get('uuid', None)
    logger.debug('/create_job: name: {}, uuid: {}'.format(name, uuid))

    job = db_api.insert_new_job(uuid=uuid,
                                name=name,
                                payload_text=request.form.get('payload_text', None),
                                status=request.form.get('status', None))
    return jsonify(job.as_json())


@job_status_handler.route('/create_task', methods=['POST'])
def create_task():
    """Create task."""
    job_id = request.form.get('job_id', None)
    logger.debug('/create_task: job_id: {}'.format(job_id))

    task = db_api.insert_new_task(job_id=job_id,
                                  uuid=request.form.get('uuid', None),
                                  name=request.form.get('name', None),
                                  payload_text=request.form.get('payload_text', None),
                                  status=request.form.get('status', None))
    return jsonify(task.as_json())


# ##############################################################################
# ############################# UPDATE #########################################
# ##############################################################################
@job_status_handler.route('/update_job', methods=['POST'])
def update_job():
    """Update job."""
    job_id = request.form.get('job_id', None)
    uuid = request.form.get('uuid', None)
    name = request.form.get('name', None)
    payload_text = request.form.get('payload_text', None)
    status = request.form.get('status', None)
    logger.debug('/update_job: job_id: {}, uuid: {}, name: {}, status: {}, payload_text: {}'
                 .format(job_id, uuid, name, status, payload_text))

    job = db_api.update_job(job_id=job_id,
                            uuid=uuid,
                            name=name,
                            payload_text=payload_text,
                            status=status)
    return jsonify(job.as_json())


@job_status_handler.route('/update_task', methods=['POST'])
def update_task():
    """Update task."""
    task_id = request.form.get('task_id', None)
    uuid = request.form.get('uuid', None)
    name = request.form.get('name', None)
    payload_text = request.form.get('payload_text', None)
    status = request.form.get('status', None)
    update_parent_job = request.form.get('update_parent_job', None)
    logger.debug('/update_task: task_id: {}, uuid: {}, name: {}, status: {}, payload_text: {}, update_parent_job: {}'
                 .format(task_id, uuid, name, status, payload_text, update_parent_job))

    task = db_api.update_task(task_id=task_id,
                              uuid=uuid,
                              name=name,
                              payload_text=payload_text,
                              status=status,
                              update_parent_job=update_parent_job)
    return jsonify(task.as_json())


# ##############################################################################
# ############################# READ ###########################################
# ##############################################################################
@job_status_handler.route('/read_job', methods=['GET'])
def read_job():
    """Read job."""
    job_id = request.args['job_id']
    logger.debug('/read_job: job_id: {}'.format(job_id))

    job = db_api.select_job_from_id(job_id)
    return jsonify(job.as_json())


@job_status_handler.route('/read_all_jobs', methods=['GET'])
def read_all_jobs():
    """Read all jobs."""
    logger.debug('/read_all_jobs')

    jobs = db_api.select_job_all()
    jobs = [job.as_json() for job in jobs]
    return jsonify(jobs)


@job_status_handler.route('/read_task', methods=['GET'])
def read_task():
    """Read task."""
    task_id = request.args.get('task_id', None)
    logger.debug('/read_task: task_id: {}'.format(task_id))

    if task_id is None:
        raise ValueError('task_id is None at /read_task')
    task = db_api.select_task_from_id(task_id)
    return jsonify(task.as_json())


@job_status_handler.route('/read_task_from_uuid', methods=['GET'])
def read_task_from_uuid():
    """Read task from uuid."""
    task_uuid = request.args.get('task_uuid', None)
    logger.debug('/read_task: task_uuid: {}'.format(task_uuid))

    if task_uuid is None:
        raise ValueError('task_uuid is None at /read_task')
    task = db_api.select_task_from_uuid(task_uuid)
    return jsonify(task.as_json())
