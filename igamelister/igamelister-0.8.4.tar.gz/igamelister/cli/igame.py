import sys

import click

from igamelister.cli.packages import Packages
from igamelister.cli.slaves import Slaves


class Igame:

    PACKAGES_DATA_FILE = "packages.dat"
    SLAVES_DATA_FILE = "slaves.dat"

    def __init__(self, config):
        self.packages_data = Packages(config)
        self.slaves_data = Slaves(config)

    def load(self):
        try:
            self.packages_data.load(readonly=True)
        except ValueError:
            raise

        try:
            self.slaves_data.load(readonly=True)
        except ValueError:
            raise

    #
    # Click command methods
    #

    def cli_igame_gameslist(self):
        if len(self.packages_data.data) == 0 or len(self.slaves_data.data) == 0:
            sys.exit(1)

        click.echo("todo!")

    def cli_igame_genres(self):
        if len(self.packages_data.data) == 0 or len(self.slaves_data.data) == 0:
            sys.exit(1)

        click.echo("todo!")
