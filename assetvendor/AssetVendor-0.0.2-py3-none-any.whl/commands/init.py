from .base import Command


class Init(Command):
    """
    Generate
    """

    def add_arguments(self, parser):
        parser.add_argument('root_dir', metavar="ROOT_DIR", nargs='?', default='.')

        config = parser.add_mutually_exclusive_group(required=False)
        config.add_argument('--json', dest='config', action='store_const', const='json', default='json',
                            help="Write the config file using the JSON format.")
        config.add_argument('--yaml', dest='config', action='store_const', const='yaml',
                            help="Write the config file using the YAML format.")

    def handle(self, options):
        pass
