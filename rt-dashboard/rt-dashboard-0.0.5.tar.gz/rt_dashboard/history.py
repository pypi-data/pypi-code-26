import datetime
from collections import defaultdict

import pytz

from redis_tasks.conf import settings
from redis_tasks.registries import failed_task_registry, finished_task_registry
from redis_tasks.utils import utcnow


def jsdate(d):
    t = list(d.timetuple()[:6])
    # In js, January is 0
    t[1] -= 1
    return 'new Date{}'.format(tuple(t))


def task_tooltip(t):
    return f'''
    <b>{t.description}</b><br>
    {t.started_at:%H:%M:%S} - {t.ended_at:%H:%M:%S}<br>
    Duration: {t.ended_at - t.started_at}<br>
    <i>{t.status}</i><br>
    '''


def get_history_context():
    tz = pytz.timezone(settings.TIMEZONE)
    tasks = finished_task_registry.get_tasks() + failed_task_registry.get_tasks()
    start = utcnow() - datetime.timedelta(days=2)
    tasks = [t for t in tasks if t.started_at > start]
    tasks.sort(key=lambda t: t.started_at)

    by_func = defaultdict(list)
    for t in tasks:
        if t.started_at:
            t.started_at = t.started_at.astimezone(tz)
        if t.ended_at:
            t.ended_at = t.ended_at.astimezone(tz)
        if t.enqueued_at:
            t.enqueued_at = t.enqueued_at.astimezone(tz)
        by_func[t.func_name].append(t)

    # reconstruct worker-mapping
    for group in by_func.values():
        workers = []
        for task in sorted(group, key=lambda t: t.started_at):
            workers = [
                None if not t or t.ended_at <= task.started_at else t
                for t in workers
            ]
            try:
                task.worker = workers.index(None)
                workers[task.worker] = task
            except ValueError:
                task.worker = len(workers)
                workers.append(task)

    groups = sorted(
        by_func.values(),
        key=lambda group_tasks: (
            min(t.started_at.timetuple()[3:] for t in group_tasks),
            max(t.ended_at - t.started_at for t in group_tasks)
        ))
    groups = ",\n".join(
        "{{id: '{0}', content: '{0}', order: {1}}}".format(group_tasks[0].func_name, i)
        for i, group_tasks in enumerate(groups))

    collapsed_groups = {k for k, v in by_func.items()
                        if len(v) / len(tasks) < 0.02}

    rows = []
    for t in tasks:
        keys = {
            'group': t.func_name,
            'subgroup': t.worker,
            'start': t.started_at,
            'title': task_tooltip(t),
        }
        if (t.func_name not in collapsed_groups or
                (t.ended_at - t.started_at) > datetime.timedelta(minutes=1)):
            keys.update({
                'end': t.ended_at,
                'type': 'range',
                'content': '[{}]'.format(t.ended_at - t.started_at),
            })
        else:
            keys.update({
                'type': 'point',
                'content': t.started_at.strftime('%H:%M:%S'),
            })

        if t.status != 'finished':
            keys['style'] = 'border-color: {0}; background-color: {0}'.format('#E69089')

        keys = {k: jsdate(v) if isinstance(v, datetime.datetime) else repr(v)
                for k, v in keys.items()}
        rows.append('{' + ','.join('{}: {}'.format(k, v) for k, v in keys.items()) + '}')
    rowtext = ",\n".join(rows)

    return dict(rows=rowtext, groups=groups)
