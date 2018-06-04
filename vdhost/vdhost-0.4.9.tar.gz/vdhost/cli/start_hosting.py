import click
import subprocess
import os

from colored import fg
from colored import stylize


@click.command(name='start-hosting')
def start_hosting():
    """
    args: None |
    Runs the Vectordash client on the host's machine

    """
    try:
        # Path to vectordash directory
        var_folder = os.path.expanduser('/var/')
        var_vd_folder = os.path.expanduser(var_folder + 'vectordash/')

        if not os.path.isfile(var_vd_folder + 'install_complete'):
            print(stylize("Please run 'vdhost install' first!", fg("red")))
            return

        print(stylize("Launching the Vectordash client on this machine", fg("green")))

        # If directories don't exist, exit the program and instruct user to run 'vdhost install'
        if not os.path.isdir(var_folder) or not os.path.isdir(var_vd_folder):
            print(stylize("Could not launch", fg("red")))
            print(stylize("Are you sure have run: ", fg("red")), stylize("vdhost install", fg("blue")))
            print(stylize("If not, please navigate to the vectordash-host directory and run that command", fg("red")))
            return

        # Client file and its dependencies - should all be in /var/vectordash/
        client_py = os.path.expanduser(var_vd_folder + 'client.py')
        sshtunnel_py = os.path.expanduser(var_vd_folder + 'SSHtunnel.py')
        networkingprotocol_py = os.path.expanduser(var_vd_folder + 'NetworkingProtocol.py')
        specs_py = os.path.expanduser(var_vd_folder + 'specs.py')
        containercontroller_py = os.path.expanduser(var_vd_folder + 'ContainerController.py')
        helper_py = os.path.expanduser(var_vd_folder + 'helper.py')

        # If any of the client files are missing, program will not execute
        if not os.path.isfile(client_py) or not os.path.isfile(sshtunnel_py) or not os.path.isfile(specs_py) or \
                not os.path.isfile(networkingprotocol_py) or not os.path.isfile(containercontroller_py) or \
                not os.path.isfile(helper_py):
            print(stylize("It seems as though you have not downloaded one or more the following files:", fg("red")))

            print(stylize(client_py, fg("red")))
            print(stylize(sshtunnel_py, fg("red")))
            print(stylize(networkingprotocol_py, fg("red")))
            print(stylize(specs_py, fg("red")))
            print(stylize(containercontroller_py, fg("red")))

            print(stylize("Please go to https://vectordash.com/host/ to download them and make sure they are stored "
                          "in the appropriate directory: " + var_vd_folder, fg("red")))
            return

        if not os.path.isfile("/etc/supervisor/conf.d/vdclient.conf"):
            print(stylize("Something went wrong during the install. Please try running 'vdhost install' again."))
            return

        else:
            try:
                # Run the client script
                #args = ['python3', client_py]
                #subprocess.check_call(args)
                subprocess.call("sudo supervisorctl start vdclient", shell=True) 
            
            except subprocess.CalledProcessError:
                print("It looks as if your files have been corrupted. Please go to https://vectordash.com/host/ "
                      "to re-download the package and move the files to the appropriate directory: " + var_vd_folder)

            except PermissionError:
                print("You do not have permission to execute this. Try re-running the command as sudo: "
                      + stylize("sudo vdhost start-hosting", fg("blue")))

    except ValueError as e:
        print(stylize("The following error was encountered: ", fg("red")) + str(e))
        print(stylize("The Vectordash client could not be launched. Please make a github pull request with your error.",
                      fg("red")))
