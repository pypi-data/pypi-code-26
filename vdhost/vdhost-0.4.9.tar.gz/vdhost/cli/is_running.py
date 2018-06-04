import click
import subprocess
import os

from colored import fg
from colored import stylize


@click.command(name='is-running')
def is_running():
    """
    args: None |
    Checks if the Vectordash client is running on the host's machine

    """
    try:
        print(stylize("Checking...", fg("green")))

        # Path to vectordash directory
        var_folder = os.path.expanduser('/var/')
        var_vd_folder = os.path.expanduser(var_folder + 'vectordash/')

        if not os.path.isfile(var_vd_folder + 'install_complete'):
            print(stylize("Please run 'vdhost install' first!", fg("red")))
            return

        # Client file and its dependencies - should all be in /var/vectordash/
        #client_py = os.path.expanduser(var_vd_folder + 'client.py')
        #sshtunnel_py = os.path.expanduser(var_vd_folder + 'SSHtunnel.py')
        #networkingprotocol_py = os.path.expanduser(var_vd_folder + 'NetworkingProtocol.py')
        #specs_py = os.path.expanduser(var_vd_folder + 'specs.py')
        #containercontroller_py = os.path.expanduser(var_vd_folder + 'ContainerController.py')
        #helper_py = os.path.expanduser(var_vd_folder + 'helper.py')

        # If any of the client files are missing, program will not execute
        #if not os.path.isfile(client_py) or not os.path.isfile(sshtunnel_py) or not os.path.isfile(specs_py) or \
        #        not os.path.isfile(networkingprotocol_py) or not os.path.isfile(containercontroller_py) or \
        #        not os.path.isfile(helper_py):
        #    print(stylize("The Vectordash hosting client is NOT running on this machine. You are missing a file(s)", fg("red")))
        #    return
        #else:
        #    try:
                # Check if it is running
                #ps_args = ['ps', '-ax']
                #ps = subprocess.Popen(ps_args, stdout=subprocess.PIPE)
                #grep_py3 = subprocess.Popen(['grep', 'python3'], stdin=ps.stdout, stdout=subprocess.PIPE)
                #ps.stdout.close()
                #grep_cli = subprocess.Popen(['grep', 'client.py'], stdin=grep_py3.stdout, stdout=subprocess.PIPE)
                #grep_py3.stdout.close()

                #is_running_output = grep_cli.communicate()[0].decode("utf-8")

                #if is_running_output != "":
        
        client_running_file = os.path.expanduser(var_vd_folder + 'client_running')
        
        if os.path.exists(client_running_file):

            f = open(client_running_file, 'r')
            p = f.read()
            f.close()
            
            if int(p) != -1:
                print(stylize("The Vectordash hosting client is currently running on this machine", fg("green")))

            else:
                print(stylize("The Vectordash hosting client is NOT running on this machine", fg("red")))

        else:
            print("Something went wrong in the install step. Please try running 'vdhost install' again.")

    except ValueError as e:
        print(stylize("The following error was encountered: ", fg("red")) + str(e))
