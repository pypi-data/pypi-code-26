from abc import ABC
from functools import lru_cache
import string


class Template(ABC):
    """Nginx configuration file template.
    Template should be given as docstring with parameters
    enclosed in <pointy> brackets.
    """

    _ESCAPE_TABLE = str.maketrans({
            "<": "{",
            ">": "}",
            "{": "<",
            "}": ">",
        })

    def __init__(self):
        self.parameters_extractor = ParametersExtractor(self)
        self._template_str = self.__doc__.translate(Template._ESCAPE_TABLE)

    def format(self, **kwargs):
        """Returns template formatted with requrired arguments.
        Argument list is extracted from the template string
        (arguments are enclosed in <pointy> brackets).
        """

        missing_keys = [param for param in self.parameters
                        if param not in kwargs]
        if missing_keys:
            class_name = self.__class__.__name__
            raise TypeError("{}.format() requires {}. Missing parameters: {}.".format(
                class_name, ", ".join(self.parameters), ", ".join(missing_keys)))

        filled_template = self._template_str.format_map(kwargs)
        return filled_template.translate(Template._ESCAPE_TABLE)

    @property
    @lru_cache(maxsize=1)
    def parameters(self):
        return self.parameters_extractor.extract()


class ParametersExtractor:
    __formatter = string.Formatter()

    def __init__(self, template):
        self.template = template

    def extract(self):
        template_str = self.template._template_str
        parsed_docstring = ParametersExtractor.__formatter.parse(template_str)
        parameters = [parameter
                      for (_, parameter, _, _) in parsed_docstring
                      if parameter]
        return ParametersExtractor.__sorted_parameters(parameters)

    @staticmethod
    def __sorted_parameters(parameters):
        parameters_set = set(parameters)
        if "domain" in parameters_set:
            parameters.remove("domain")
            parameters.insert(0, "domain")
        if "port" in parameters_set:
            parameters.remove("port")
            parameters.insert(0, "port")
        return parameters
