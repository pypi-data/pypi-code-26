import collections
import importlib
import re
import sys


TEST_MODULE = re.compile(r'tests\.((?:\w+\.)*)test_(\w+)')


class DivideAndCoverConfig(collections.namedtuple(
        'DivideAndCoverConfig', 'auto_detect modules')):

    @classmethod
    def from_dict(cls, dct):
        dct = dict(dct)
        config = cls(auto_detect=dct.pop('auto_detect', True),
                     modules=dct.pop('modules', ()))
        for key in sorted(dct):
            print('Unexpected Divide and Cover config key: {}'.format(key))
        return config


def module_path(test_module_path, test_module):
    config = DivideAndCoverConfig.from_dict(
        getattr(test_module, 'DIVIDE_AND_COVER_CONFIG', {}))
    if config.auto_detect:
        match = TEST_MODULE.fullmatch(test_module_path)
        if match:
            yield ''.join(match.groups())
    for module in config.modules:
        yield module


def pytest_addoption(parser):
    parser.addoption('--divide-and-cover', action='store_true',
                     help='activate divide and cover tracing')


class DivideAndCoverPlugin(object):

    fiddle_with_coverage = False

    def __init__(self, modules, importer):
        self.modules = modules
        self.importer = importer

    @property
    def coverage_handler(self):
        return self.importer('divide_and_cover.coverage_handler')

    def pytest_configure(self, config):
        if config.option.divide_and_cover:
            if self.coverage_handler.UNDER_WRAPPER:
                self.fiddle_with_coverage = True
            else:
                print('Warning: called with --divide-and-cover, but not '
                      'running under divide_and_cover. Not activating plugin.')

    def pytest_collection_modifyitems(self, session, config, items):
        if self.fiddle_with_coverage:
            coverage_script = self.coverage_handler.coverage_script
            modules = self.modules.copy()
            paths = []
            for test_path, module in modules.items():
                module_paths = []
                for module_path_ in module_path(test_path, module):
                    paths.append(module_path_)
                    module_paths.append(module_path_)
                coverage_script.new_coverage(test_path, module_paths)
            for path in paths:
                try:
                    self.importer(path)
                except ImportError:
                    print('Could not import {}'.format(path))

    def pytest_runtest_setup(self, item):
        if self.fiddle_with_coverage:
            self.coverage_handler.coverage_script.activate_coverage(
                item.obj.__module__)

    def pytest_runtest_teardown(self, item, nextitem):
        if self.fiddle_with_coverage:
            self.coverage_handler.coverage_script.deactivate_coverage()


PLUGIN = DivideAndCoverPlugin(sys.modules, importlib.import_module)

pytest_configure = PLUGIN.pytest_configure
pytest_collection_modifyitems = PLUGIN.pytest_collection_modifyitems
pytest_runtest_setup = PLUGIN.pytest_runtest_setup
pytest_runtest_teardown = PLUGIN.pytest_runtest_teardown
