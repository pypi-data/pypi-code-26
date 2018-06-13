import textwrap
import yaml


class KookiException(Exception):
    pass


class NoConfigFileFound(KookiException):

    message = textwrap.dedent('''\
        No '{}' file found.
        Create one by executing 'kooki new'.''')

    def __init__(self, config_file_name):
        message = self.message.format(config_file_name)
        super().__init__(message)


class YamlErrorConfigFileParsing(KookiException):

    message = textwrap.dedent('''\
        Yaml error during config file parsing.
        Please check the format of your config file.''')

    def __init__(self, exc):
        message = self.message
        super().__init__(message)


class YamlErrorConfigFileBadType(KookiException):

    message = textwrap.dedent('''\
        The Yaml parsed should be a dict and it is a {}.
        Please check the format of your config file.''')

    def __init__(self, type_found):
        message = self.message.format(type_found)
        super().__init__(message)


class MissingRecipe(KookiException):

    message = textwrap.dedent('''\
        Cannot find recipe '{}'.
        Is it installed ? Try to run kooki bake with --update.
        Please check the recipe of your config file.''')

    def __init__(self, recipe):
        message = self.message.format(recipe)
        super().__init__(message)


class InvalidRecipe(KookiException):

    message = textwrap.dedent('''\
        The recipe '{}' seems to be invalid.
        Please check this error with the author of this recipe.
        Give him the following message:
        {}''')

    def __init__(self, recipe, error):
        message = self.message.format(recipe, error)
        super().__init__(message)


class MissingJar(KookiException):

    message = textwrap.dedent('''\
        Cannot find jar '{}'.
        Is it installed ? Try to run kooki bake with --update.
        Please check the jar of your config file.''')

    def __init__(self, jar):
        message = self.message.format(jar)
        super().__init__(message)


class MissingResource(KookiException):

    message = textwrap.dedent('''\
        Cannot find {0} '{1}' in the following directory:
        {2}
        Please check the {0} of your config file.''')

    def __init__(self, jars, recipe, resource_name, resource):
        from kooki.jars import get_search_paths
        directories = get_search_paths(jars, recipe)
        directories_str = '\n'.join(['- {}'.format(directory) for directory in directories])
        message = self.message.format(resource_name, resource, directories_str)
        super().__init__(message)


class MissingTemplate(MissingResource):

    def __init__(self, jars, recipe, template):
        super().__init__(jars, recipe, 'template', template)


class MissingMetadata(MissingResource):

    def __init__(self, jars, recipe, metadata):
        super().__init__(jars, recipe, 'metadata', metadata)


class MissingContent(MissingResource):

    def __init__(self, jars, recipe, content):
        super().__init__(jars, recipe, 'content', content)


class BadMetadata(KookiException):

    message = textwrap.dedent('''\
        Missing metadata, check the list above.''')

    def __init__(self):
        message = self.message
        super().__init__(message)


class TooMuchResult(KookiException):

    message = textwrap.dedent('''\
        Too much files match the name provided ({})
        {}
        You should provide the full name with the file extension.''')

    def __init__(self, name, result):
        message = self.message.format(name, yaml.dump(result, default_flow_style=False)[:-1])
        super().__init__(message)
