import json
import mimetypes
import os.path
from functools import wraps
from math import ceil
from operator import itemgetter
from threading import local

import jinja2
from redis_tasks import Queue
from redis_tasks.registries import (
    failed_task_registry, finished_task_registry, worker_registry)
from redis_tasks.task import Task
from redis_tasks.worker import Worker
from werkzeug import Headers, Response, routing

from .history import get_history_context


def jsonify(f):
    @wraps(f)
    def _wrapped(*args, **kwargs):
        result_dict = f(*args, **kwargs)
        return Response(json.dumps(result_dict), mimetype='application/json')
    return _wrapped


def send_file(filename, mimetype=None):
    attachment_filename = os.path.basename(filename)

    if mimetype is None:
        mimetype = mimetypes.guess_type(attachment_filename)[0] \
            or 'application/octet-stream'

    headers = Headers()
    mtime = os.path.getmtime(filename)
    fsize = os.path.getsize(filename)
    headers['Content-Length'] = fsize

    with open(filename, 'rb') as f:
        data = f.read()
    rv = Response(data, mimetype=mimetype, headers=headers)
    rv.last_modified = mtime
    return rv


class WebApp:
    def __init__(self):
        self.routes = routing.Map()
        self.view_functions = dict()
        root_path = os.path.dirname(__file__)
        self.context = local()
        self.static_path = os.path.join(root_path, 'static')
        self.add_url_rule(
            '/static/<path:filename>',
            endpoint='static',
            view_func=self.static
        )
        self.environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.join(root_path, 'templates')),
        )

    def get_response(self, server_name, path, base_path='', method="GET"):
        self.context.adapter = self.routes.bind(server_name, path_info=path)
        self.context.base_path = base_path
        rv = self.context.adapter.dispatch(
            lambda e, v: self.view_functions[e](**v),
            method=method)
        if isinstance(rv, routing.RequestRedirect):
            rv.new_url = base_path + '/' + '/'.join(rv.new_url.split('/')[3:])
            return rv.get_response(None)
        else:
            return rv

    def static(self, filename):
        return send_file(os.path.join(self.static_path, filename))

    def route(self, rule, **options):
        def decorator(f):
            self.add_url_rule(rule, f, **options)
            return f
        return decorator

    def add_url_rule(self, rule, view_func=None, endpoint=None, **options):
        if not endpoint:
            endpoint = view_func.__name__
        methods = options.pop('methods', ('GET', ))

        rule = routing.Rule(rule, methods=methods, endpoint=endpoint, **options)
        self.routes.add(rule)
        self.view_functions[endpoint] = view_func

    def url_for(self, endpoint, **values):
        if endpoint.startswith('.'):
            endpoint = endpoint[1:]
        return self.context.base_path + self.context.adapter.build(endpoint, values)

    def render_template(self, template_name, **context):
        template = self.environment.get_template(template_name)
        context['url_for'] = self.url_for
        return Response(template.render(context), content_type='text/html')


app = WebApp()


def serialize_date(dt):
    if dt:
        return dt.isoformat()
    else:
        return dt


def serialize_job(job):
    return dict(
        id=job.id,
        status=job.status,
        enqueued_at=serialize_date(job.enqueued_at),
        started_at=serialize_date(job.started_at),
        ended_at=serialize_date(job.ended_at),
        origin=job.origin,
        error_message=job.error_message,
        description=job.description)


def remove_none_values(input_dict):
    return dict(((k, v) for k, v in input_dict.items() if v is not None))


def pagination_window(total_items, cur_page, per_page=5, window_size=10):
    all_pages = range(1, int(ceil(total_items / float(per_page))) + 1)
    result = all_pages
    if window_size >= 1:
        temp = min(
            len(all_pages) - window_size,
            (cur_page - 1) - int(ceil(window_size / 2.0))
        )
        pages_window_start = max(0, temp)
        pages_window_end = pages_window_start + window_size
        result = all_pages[pages_window_start:pages_window_end]
    return result


@app.route('/', defaults={'queue_name': '[running]', 'page': '1'})
@app.route('/<queue_name>', defaults={'page': '1'})
@app.route('/<queue_name>/<page>')
def overview(queue_name, page):
    queue = Queue(queue_name)

    return app.render_template(
        'rt_dashboard/dashboard.html',
        workers=Worker.all(),
        queue=queue,
        page=page,
        queues=Queue.all(),
        rt_url_prefix=app.url_for('overview'),
        poll_interval=2500,
    )


@app.route('/history')
def history():
    return app.render_template(
        'rt_dashboard/history.html',
        **get_history_context()
    )


@app.route('/job/<job_id>/cancel', methods=['POST'])
@jsonify
def cancel_job_view(job_id):
    Task.fetch(job_id).cancel()
    return dict(status='OK')


@app.route('/queue/<queue_name>/empty', methods=['POST'])
@jsonify
def empty_queue(queue_name):
    if queue_name == '[failed]':
        queue = failed_task_registry
    elif queue_name == '[finished]':
        queue = finished_task_registry
    else:
        queue = Queue(queue_name)
    queue.empty()
    return dict(status='OK')


@app.route('/queue/<queue_name>/delete', methods=['POST'])
@jsonify
def delete_queue(queue_name):
    queue = Queue(queue_name)
    queue.delete()
    return dict(status='OK')


@app.route('/queues.json')
@jsonify
def list_queues():
    return {'queues': [
        {'name': '[failed]',
         'count': failed_task_registry.count(),
         'url': app.url_for('overview', queue_name='[failed]')},
        {'name': '[finished]',
         'count': finished_task_registry.count(),
         'url': app.url_for('overview', queue_name='[finished]')},
        {'name': '[running]',
         'count': len(worker_registry.get_running_tasks()),
         'url': app.url_for('overview', queue_name='[running]')},
    ] + [
        {'name': q.name,
         'count': q.count(),
         'url': app.url_for('overview', queue_name=q.name)}
        for q in Queue.all()
    ]}


@app.route('/jobs/<queue_name>/<page>.json')
@jsonify
def list_jobs(queue_name, page):
    if queue_name != '[running]':
        if queue_name == '[failed]':
            queue = failed_task_registry
        elif queue_name == '[finished]':
            queue = finished_task_registry
        else:
            queue = Queue(queue_name)

        current_page = int(page)
        per_page = 20
        total_items = queue.count()
        pages_numbers_in_window = pagination_window(
            total_items, current_page, per_page)
        pages_in_window = [
            dict(number=p, url=app.url_for('overview', queue_name=queue_name, page=p))
            for p in pages_numbers_in_window
        ]
        last_page = int(ceil(total_items / float(per_page)))

        prev_page = None
        if current_page > 1:
            prev_page = dict(url=app.url_for(
                'overview', queue_name=queue_name, page=(current_page - 1)))

        next_page = None
        if current_page < last_page:
            next_page = dict(url=app.url_for(
                'overview', queue_name=queue_name, page=(current_page + 1)))

        pagination = remove_none_values(
            dict(
                pages_in_window=pages_in_window,
                next_page=next_page,
                prev_page=prev_page
            )
        )

        offset = (current_page - 1) * per_page
        jobs = [serialize_job(job) for job in queue.get_tasks(offset, per_page)]
    else:
        jobs = sorted((
            {**serialize_job(Task.fetch(tid)),
             'worker': Worker.fetch(wid).description}
            for wid, tid in worker_registry.get_running_tasks().items()),
            key=itemgetter('worker'),
        )
        pagination = {}
    return dict(name=queue_name, jobs=jobs, pagination=pagination)


@app.route('/workers.json')
@jsonify
def list_workers():
    return {'workers': [
        {
            'name': worker.description,
            'queues': [q.name for q in worker.queues],
            'state': str(worker.state),
        }
        for worker in Worker.all()
    ]}
