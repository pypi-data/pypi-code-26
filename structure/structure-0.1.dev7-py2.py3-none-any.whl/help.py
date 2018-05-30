import sys

if sys.version_info[0] < 3:
  from utils import green
else:
  from structure.utils import green


class HelpCommand(object):

  @staticmethod
  def text():
    return '''     
  Usage:        {} <command> [arguments]

  Commands:

    deploy      [name] [type]    Deploy the current folder to a Structure app
    list | ls                    List all apps

    create                       Create a new app on Structure
    remove      [name]           Remove an existing app

    logs        [name]           View a running app's logs

    run         [name]           Run an app
    stop        [name]           Stop an app
    restart     [name]           Restart an app

    ssh         [name]           SSH into an app's filesystem
    ssh-add     [name]           Add an SSH public key to an app
    token                        See your API token

  --------------

  Documentation and tutorials: {}

  Examples:

    - Create a new app
      $ structure create

    - Run an existing app:
      $ structure run hello-world

    - Deploy an update to an existing app:
      $ structure deploy hello-world
    '''.format(
        green('structure'),
        green('https://docs.structure.sh')
    )
