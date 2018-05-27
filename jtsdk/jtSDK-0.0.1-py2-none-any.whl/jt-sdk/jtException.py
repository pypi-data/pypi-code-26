class jtException(Exception):

    def __init__(self, status_code, error_message):
        self.status_code = status_code
        self.error_message = error_message

    def __str__(self):
        return self.error_message
