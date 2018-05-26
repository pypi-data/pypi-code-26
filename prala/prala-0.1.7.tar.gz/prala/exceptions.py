
class EmptyDictionaryError(Exception):
    message="The dict is empty ..."
    def __init__(self, dict_file_name, part_of_speach, extra_filter):
        super().__init__(type(self).message)
        self.dict_file_name=dict_file_name
        self.part_of_speach = part_of_speach
        self.extra_filter = extra_filter

class NoDictionaryError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.dict_file_name=message.filename
        self.dict_message=message.strerror