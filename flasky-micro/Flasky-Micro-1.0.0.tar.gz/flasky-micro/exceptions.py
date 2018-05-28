import os


class FlaskyException(Exception):
    pass


class ConfigurationException(FlaskyException):
    pass


class FileNotFoundException(FlaskyException):

    def __init__(self, file):
        super().__init__("File not found - File=[%s]" % file)
        self.file = file


class KeyNotFoundException(FlaskyException):

    def __init__(self, key):
        super().__init__("Key not found - Key=[%s]" % ".".join(key))
        self.key = key


class FormatValueException(FlaskyException):

    def __init__(self, value):
        super().__init__("Cannot format value - Value=[%s]" % value)
        self.value = value


class ParameterNotFoundException(FlaskyException):
    def __init__(self, name):
        super().__init__("Parameter '%s' not found" % name)
        self.name = name


class InvalidParameterException(FlaskyException):
    def __init__(self, name, value):
        super().__init__("Parameter '%s' is invalid - Value=[%s]" % (name, value))
        self.name = name


class Traceback:

    def __init__(self, class_name, message):
        self.class_name = class_name
        self.message = message
        self.files = []

    def add_file(self, name, line=0):
        file = TracebackFile(name, line)
        self.files.append(file)

    def __str__(self):
        files_stack = ", ".join(["%s@Line %s" % (f.name, f.line) for f in reversed(self.files)])
        traceback_message = "[%s] - %s - %s" % (self.class_name, self.message, files_stack)
        return traceback_message


class TracebackFile:

    def __init__(self, name, line):
        self.name = name
        self.line = line


def get_traceback(ex):
    traceback = Traceback(
        class_name=ex.__class__.__name__,
        message=str(ex).replace("\r", "").replace("\n", "").replace("\t", " ")
    )

    ex_traceback = ex.__traceback__
    while ex_traceback is not None:
        filename = os.path.basename(ex_traceback.tb_frame.f_code.co_filename)
        line = ex_traceback.tb_lineno
        traceback.add_file(filename, line)
        ex_traceback = ex_traceback.tb_next if ex_traceback.tb_next is not None else None

    return traceback
