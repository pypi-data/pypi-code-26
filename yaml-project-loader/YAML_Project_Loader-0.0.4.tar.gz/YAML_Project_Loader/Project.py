import yaml
from ContextLoader import ContextLoader
import collections
import os


# Taken from https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
def dict_merge(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.iteritems():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


class Project:

    def __init__(self, root_path):
        """
        Main class to handle project YAML data

        :param root_path: Absolute path to project root
        """
        self._root = root_path
        self._yaml_project = None
        self.configs = {}
        self._contexts = {}

    def get_name(self):
        """
        Retrieves the project's name
        :return: Project's name as string
        """
        return self._yaml_project['name']

    def _get_expanded_yaml(self):
        """
        Creates a new dictionary overwriting the 'config' with all references resolved for plugins and contexts.

        :return: Copy of the original YAML project included resolved references
        """
        base_yaml = dict(self._yaml_project)
        base_yaml['configs'] = dict(self.configs)
        return base_yaml

    def read(self):
        """
        Steps when loading a project are:
        1. Base configurations for plugins are loaded
        2. Base contexts are loaded
        3. For each export configuration:
           1. Copy the context
           2. Copy the plugin configurations
           3. Apply overrides in plugins if the context defines them

        :return: String cointaining the fully merged YAML project configuration
        """

        self._load_root()
        self._load_contexts()
        self.configs = {e: self._expand_export_configurations(self._yaml_project, e) for e in
                        self._yaml_project['configs']}
        self._override_plugin_configurations_with_context()
        return self._get_expanded_yaml()

    def _load_root(self):
        with open(os.path.join(self._root, 'project.yaml')) as cosmos_project_file:
            self._yaml_project = yaml.load(cosmos_project_file, Loader=yaml.CLoader)

    def _override_plugin_configurations_with_context(self):
        for e in self.configs:
            try:
                plugins_overrides = self.configs[e]['context']['plugins_overrides']
                for name in plugins_overrides:
                    try:
                        dict_merge(self.configs[e]['plugins'][name], plugins_overrides[name])
                    except KeyError:
                        pass  # This means there is an override for an unused plugin. TODO: Should throw a warning?
            except KeyError:
                pass

    def _load_contexts(self):
        for root, _, file_names in os.walk(os.path.join(self._root, 'contexts')):
            file_names = [f for f in file_names if f.endswith('.context.yaml')]
            for f in file_names:
                context_name = f.split('.')[0]
                yaml_path = os.path.join(root, f)
                with open(yaml_path) as cf:
                    self._contexts[context_name] = yaml.load(cf, Loader=ContextLoader)
                    if self._contexts[context_name] is None:
                        self._contexts[context_name] = {}

    def _expand_export_configurations(self, project_conf, configuration_name):
        config = project_conf['configs'][configuration_name]

        plugin_conf = {}
        for p in config['plugins']:
            with open(os.path.join(self._root, 'plugins', p + '.config.yaml')) as plugin_configuration_file:
                plugin_conf[p] = yaml.load(plugin_configuration_file, Loader=ContextLoader)

        config['plugins'] = plugin_conf
        config['context'] = self._contexts[config['context']]

        return config
