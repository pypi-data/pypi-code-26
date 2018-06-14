
class OAuthException(BaseException):
    pass


class NoTokenException(BaseException):
    pass


class ConfigurationException(BaseException):
    pass


class DDSConfigurationException(ConfigurationException):
    pass


class OAuthConfigurationException(ConfigurationException):
    pass
