# exceptions.py
# Rohan Weeden
# Created: August 17, 2017


class InvalidGranuleException(Exception):
    """Custom exception thrown by the module, indicates a invalid granule string."""
    def __init__(self, string, granule_string):
        super(InvalidGranuleException, self).__init__(string)
        self.granule = granule_string


class InvalidCredentialsException(Exception):
    """Earthdata credentials were invalid when downloading granule"""
    pass
