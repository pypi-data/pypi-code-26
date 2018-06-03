from configparser import BasicInterpolation


class TemplateInterpolation(BasicInterpolation):

    def __init__(self, **kwargs):
        self._interpolate_dict = kwargs

    def set(self, key: str, value):
        self._interpolate_dict[key] = value

    def before_get(self, parser, section, option, value, defaults):
        return value % self._interpolate_dict
