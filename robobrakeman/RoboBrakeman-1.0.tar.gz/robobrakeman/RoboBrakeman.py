import docker
from robot.api import logger
from docker.types import Mount


class RoboBrakeman(object):

    def __init__(self):
        self.client = docker.from_env()
        self.brakeman_docker = "abhaybhargav/brakeman"

    def run_brakeman_against_source(self, code_path, results_path):
        self.source_path = code_path
        self.results_path = results_path
        source_mount = Mount("/src", self.source_path, type = "bind")
        results_mount = Mount("/results", self.results_path, type = "bind")
        self.client.containers.run(self.brakeman_docker, mounts = [source_mount, results_mount])
        logger.info("Successfully ran Brakeman against the src directory. Please find the results in the designated results directory")
