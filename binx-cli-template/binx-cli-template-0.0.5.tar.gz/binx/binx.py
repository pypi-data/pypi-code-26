import random
import string

def random_string(length, start = ''):
    """
    Simple function to generate an unique random string
    """
    for i in range(length):
        start += random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
    return str(start)


class Binx(object):

    prefix = None
    length = None

    def __init__(self, **kwargs):
        """
        Initialize with defaults.
        """
        for key in kwargs:
            setattr(self, key, kwargs[key])
    
    def random(self):
        """
        Generate a random string and return the value
        """
        return random_string(int(self.length), self.prefix)