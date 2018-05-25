from __future__ import absolute_import, division, print_function, unicode_literals


class ContentMissingError(Exception):
    pass


class ValidationError(Exception):
    def __init__(self):
        super(ValidationError, self).__init__(self.message)


class SingleProceduresNotFoundError(ValidationError):
    message = 'Two procedures were found in the procedure folder.  ' \
              'Only a single procedure is allowed to be saved / published at a time.'


class PublishProcedureError(ValidationError):
    def __init__(self, *args):
        self.message = self.message.format(*args)
        super(PublishProcedureError, self).__init__()


class MissingAssetDirectoryError(PublishProcedureError):
    message = 'Asset folder missing from {0}'


class MissingYamlFileError(PublishProcedureError):
    message = 'Missing Yaml file {0}'


class InvalidYamlFileError(PublishProcedureError):
    message = 'Invalid Yaml file {0}'


class CombinedValidationError(ValidationError):
    def __init__(self, errors):
        self.errors = errors
        self.message = '\n'.join(map(str, self.errors))
        super(CombinedValidationError, self).__init__()
