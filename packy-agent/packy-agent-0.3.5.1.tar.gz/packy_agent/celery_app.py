from __future__ import print_function
import sys

from celery import Celery

from packy_agent.configuration.agent.base import configuration
from packy_agent.utils.misc import dump_version, remove_upgrade_in_progress_lock


class CustomCelery(Celery):

    def gen_task_name(self, name, module):
        if self.main:
            return self.main + '.' + name

        return super(CustomCelery, self).gen_task_name(name, module)


def get_celery_app():
    agent_id = configuration.get_agent_id()
    if agent_id is None:
        return

    configuration.update_local_configuration_from_server()

    application = CustomCelery(configuration.get_tasks_prefix())
    application.config_from_object(configuration.get_celery_configuration())

    __import__('packy_agent.tasks')  # register tasks

    return application


app = get_celery_app()
remove_upgrade_in_progress_lock()
dump_version('/etc/packy-agent-version', 'PACKY_AGENT_VERSION')
if not app:
    # TODO(dmu) LOW: Provide a more elegant way to exit Celery until Agent is activated
    print('Packy Agent ID (packy.agent.agent_id) is not known (maybe agent has not '
          'been activated yet), will exit', file=sys.stderr)
    sys.exit(1)
