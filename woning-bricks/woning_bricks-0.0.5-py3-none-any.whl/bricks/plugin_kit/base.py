class BasePlugin(object):
    reference = {}

    def __init__(self, project):
        self.project = project

    def get_commands(self):
        """Returns a list of commands for the project"""
        return []

    def initialize(self):
        """Initializes the project to make sure it is ready to use the plugin

        Eg. if it needs docker-compose, make sure it is available in PATH
        """
        return []

    @staticmethod
    def build_command(commands, name, driver='local'):
        """Builds a command to be added to the pool of available commands."""
        return {
            'driver': driver,
            'name': name,
            'commands': commands
        }

    def get_reference_for(self, command):
        return self.reference.get(command, '')
