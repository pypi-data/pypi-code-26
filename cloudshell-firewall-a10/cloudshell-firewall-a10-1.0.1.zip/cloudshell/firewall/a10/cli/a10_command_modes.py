from cloudshell.cli.command_mode import CommandMode

from cloudshell.firewall.a10.helpers.exceptions import A10Exception


class A10LoadingException(A10Exception):
    """Device is not ready"""


class LoadingCommandMode(CommandMode):
    PROMPT = r'(?i)(\n|\r|^)[^>#]+?\(loading\)[>#]\s*$'
    ENTER_COMMAND = ''
    EXIT_COMMAND = ''

    def __init__(self, resource_config, api):
        """Initialize Default command mode - default command mode for A10 Shells"""

        self.resource_config = resource_config
        self._api = api
        super(LoadingCommandMode, self).__init__(
            self.PROMPT,
            self.ENTER_COMMAND,
            self.EXIT_COMMAND,
            enter_actions=self.__enter_actions
        )

    def __enter_actions(self, cli_service):
        raise A10LoadingException()


class DefaultCommandMode(CommandMode):
    PROMPT = r'(\n|\r|^)((?!\((?i)(loading|#|>)).)+?>\s*$'
    ENTER_COMMAND = ''
    EXIT_COMMAND = ''

    def __init__(self, resource_config, api):
        """Initialize Default command mode - default command mode for A10 Shells"""

        self.resource_config = resource_config
        self._api = api
        super(DefaultCommandMode, self).__init__(self.PROMPT, self.ENTER_COMMAND, self.EXIT_COMMAND)


class EnableCommandMode(CommandMode):
    PROMPT = r'(\n|\r|^)((?!\((?i)(loading|config|>|#)).)+?#\s*$'
    ENTER_COMMAND = 'enable'
    EXIT_COMMAND = 'exit'

    def __init__(self, resource_config, api):
        """Initialize Enable command mode"""

        self.resource_config = resource_config
        self._api = api
        self._enable_password = None

        super(EnableCommandMode, self).__init__(
            self.PROMPT,
            self.ENTER_COMMAND,
            self.EXIT_COMMAND,
            enter_action_map={
                "[Pp]assword":
                    lambda session, logger: session.send_line(self.enable_password, logger)
            }
        )

    @property
    def enable_password(self):
        if not self._enable_password:
            password = self.resource_config.enable_password
            self._enable_password = self._api.DecryptPassword(password).Value
        return self._enable_password


class ConfigCommandMode(CommandMode):
    PROMPT = r'(\n|\r|^)[^>#]+?\(config[^>#]+?#\s*$'
    ENTER_COMMAND = 'configure'
    EXIT_COMMAND = 'exit'

    def __init__(self, resource_config, api):
        """Initialize Config command mode"""

        self.resource_config = resource_config
        self._api = api
        super(ConfigCommandMode, self).__init__(self.PROMPT, self.ENTER_COMMAND, self.EXIT_COMMAND)


CommandMode.RELATIONS_DICT = {
    LoadingCommandMode: {
        DefaultCommandMode: {
            EnableCommandMode: {
                ConfigCommandMode: {},
            }
        }
    }
}
