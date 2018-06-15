import errno
import random
import subprocess

from mako.exceptions import MakoException, text_error_template
from mako.lookup import TemplateLookup
from mako.template import Template
import os
import pwd

from ph_confer.within_template_config import confer_instance
from ph_confer.exceptions import ConfigException

def get_temp_test_template_file(template_file):
  dirname = os.path.dirname(template_file)
  filename = os.path.basename(template_file)
  return os.path.join(
      dirname,
      '.{}{}'.format(random.randint(1, 10000), filename)
  )


def create_template_file(template_file, rendered_contents):
  """
  :param template_file: the file to write to
  :param rendered_contents: the rendered template file contents
  :return: True if the file was changed, False otherwise
  """
  try:
    os.makedirs(os.path.dirname(template_file))
  except OSError as e:
    if e.errno == errno.EEXIST:
      pass
    elif e.errno == errno.EACCES:
      raise ConfigException(
          "No permission to create the output directory "
          "at {}.".format(template_file)
      )
    else:
      raise
  try:
    try:
      with open(template_file, 'r') as f:
        old_contents = f.read()
        if old_contents == rendered_contents:
          return False
    except IOError:
      pass
    with open(template_file, 'w+') as f:
      f.seek(0)
      f.write(rendered_contents)
  except OSError as e:
    if e.errno in (errno.EACCES, errno.EPERM):
      raise ConfigException(
          "No permission to create the output template "
          "at {}. "
          "Ensure you have write access to the parent directory of the file, "
          "as well as write access to any existing file.".format(template_file)
      )
    raise
  if confer_instance.file_mode:
    try:
      os.chmod(template_file, confer_instance.file_mode)
    except OSError as e:
      if e.errno == errno.EPERM:
        raise ConfigException(
            'Could not change the file permissions of {} to {}'.format(
                template_file, confer_instance.file_mode
            )
        )
      raise
  if confer_instance.owner:
    try:
      pwnam = pwd.getpwnam(confer_instance.owner)
      os.chown(template_file, pwnam.pw_uid, pwnam.pw_gid)
    except OSError as e:
      if e.errno == errno.EPERM:
        raise ConfigException(
            'Could not change the file permissions of {} to {}'.format(
                template_file, confer_instance.file_mode
            )
        )
      raise
  return True

def run_template(template_file):
  directories = []
  cur_dir = os.path.abspath(os.path.dirname(template_file))
  while cur_dir != '/':
    directories.append(cur_dir)
    cur_dir = os.path.abspath(os.path.join(cur_dir, os.pardir))

  lookup = TemplateLookup(directories=directories)
  template = Template(filename=template_file, lookup=lookup)
  confer_instance.reset()
  confer_instance.ready = True
  temp_template_file_path = None

  try:
    try:
      rendered = template.render()
    except:
      raise ConfigException(
          "Couldn't render the template: {}".format(
              text_error_template().render())
      )
    confer_instance.check_required()
    if confer_instance.test_command:
      if '{}' not in confer_instance.test_command:
        raise MakoException(
            'You need to specify the configuration file path '
            'explicitly with {}.'
        )
      temp_template_file_path = get_temp_test_template_file(
          confer_instance.output_location
      )
      create_template_file(
          temp_template_file_path,
          rendered
      )
      test_command = confer_instance.test_command.replace(
          '{}', temp_template_file_path)
      try:
        subprocess.check_output(
            test_command,
            shell=True,
            stderr=subprocess.STDOUT
        )
      except subprocess.CalledProcessError as e:
        raise ConfigException(
            'Check command [{}] returned status code {}: {}'
              .format(test_command, e.returncode, e.output)
        )

    output_template_file_changed = create_template_file(
        confer_instance.output_location,
        rendered
    )
    if output_template_file_changed and confer_instance.reload_command:
      status_code = subprocess.call(
          confer_instance.reload_command.replace('{}', temp_template_file_path),
          shell=True
      )
      if status_code != 0:
        raise ConfigException(
            'The reload command failed with status code {}'.format(status_code)
        )
    return output_template_file_changed

  finally:
    confer_instance.ready = False
    if temp_template_file_path:
      try:
        os.remove(temp_template_file_path)
      except (AttributeError, OSError):
        pass
