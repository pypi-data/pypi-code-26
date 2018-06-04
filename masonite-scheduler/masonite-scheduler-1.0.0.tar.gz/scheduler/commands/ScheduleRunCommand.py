""" A ScheduleRunCommand Command """
from cleo import Command
from scheduler.Task import Task
import pendulum


class ScheduleRunCommand(Command):
    """
    Run the scheduled tasks

    schedule:run
    """

    def handle(self):
        from wsgi import container as app
        tasks = app.collect(Task)
        
        for task_key, task_class in tasks.items():
            # Resolve the task with the container
            task = app.resolve(task_class)

            # If the class should run then run it
            if task.should_run():
                task.handle()
