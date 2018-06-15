from ph_confer.exceptions import ConfigException


class PhConferConfig:
  def __init__(self):
    self.reset()

  def reset(self):
    self.ready = False
    self.watched_keys = []
    self.test_command = None
    self.reload_command = None
    self.owner = None
    self.file_mode = '664'
    self.output_location = None

  def check_required(self):
    if self.output_location is None:
      raise ConfigException(
          'The output location must be set from within the template.'
      )

confer_instance = PhConferConfig()


def __check_config_state():
  if not confer_instance.ready:
    raise RuntimeError(
        'You should only call confer configs '
        'from within a confer template.'
    )


def rebuild_on_key_changes(keys):
  """
  :param keys: the keys to watch.  A rebuild is triggered if any
  of these keys change.
  """
  __check_config_state()
  confer_instance.watched_keys = keys


def test_command(cmd):
  """
  :param cmd: the shell command to execute in order to test that
  the template has compiled successfully.
  For example, "nginx -t -c {}" would test the generated configuration
  before moving it to the destination.
  """
  __check_config_state()
  confer_instance.test_command = cmd


def reload_command(cmd):
  """
  :param cmd: the shell command to execute in order to activate
  the configuration.
  For example, "nginx -s reload" would reload nginx without downtime.
  """
  __check_config_state()
  confer_instance.reload_command = cmd


def file_owner(owner):
  """
  :param owner: the owner of the generated configuration file.
  """
  __check_config_state()
  confer_instance.owner = owner


def file_mode(mode):
  """
  :param mode: the file mode (equivalent to chmod) of the generated
  configuration file.
  """
  __check_config_state()
  if not isinstance(mode, int):
    mode = int(mode, 8)
  confer_instance.file_mode = int(mode)


def file_location(loc):
  """
  :param loc: the location at which to put the compiled
  configuration file.
  """
  __check_config_state()
  confer_instance.output_location = loc
