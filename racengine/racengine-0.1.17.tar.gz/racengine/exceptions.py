class SMTPException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ConfigException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)