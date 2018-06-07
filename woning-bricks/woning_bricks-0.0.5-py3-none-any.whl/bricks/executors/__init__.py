from bricks.exceptions import DriverNotRecognizedError
from bricks.executors.docker import DockerComposeExecutor
from bricks.executors.local import LocalExecutor


def get_executor(driver, project):
    if driver == 'local':
        return LocalExecutor(project)
    elif driver == 'docker':
        return DockerComposeExecutor(project)
    else:
        raise DriverNotRecognizedError(driver)
