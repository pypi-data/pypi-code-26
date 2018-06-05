from django.utils.deconstruct import deconstructible
from django.core.exceptions import ValidationError


@deconstructible
class BlackListValidator:
    MESSAGE = 'not allowed.'
    CODE = 'invalid'

    def __init__(self, black_list=None, message=None, code=None):
        self.black_list = black_list if black_list is not None else []
        self.message = message if message is not None else self.MESSAGE
        self.code = code if code is not None else self.CODE

    def __call__(self, value):
        if value in self.black_list:
            raise ValidationError(self.message, self.code)
