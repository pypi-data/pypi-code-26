import os.path


class Config:
    def __init__(self, filepath, filetype):
        self.filepath = filepath
        self.filetype = filetype
        self.loader = None
        self.dumper = None
        self.config = None

        if filetype == 'json':
            import json
            self.loader, self.dumper = json.load, json.dump
        elif filetype == 'yaml':
            from . import yaml
            self.loader, self.dumper = yaml.load, yaml.dump

        with open(self.filepath) as file:
            self.config = self.loader(file)

    @property
    def registry(self):
        return self.config.get('registry')

    @property
    def location_dir(self):
        return os.path.abspath(self.config['location'])

    @property
    def metadata_dir(self):
        return os.path.abspath(self.config.get('metadata', '.vendor'))

    @property
    def packages(self):
        return self.config['packages']
