import click
import subprocess
import os

from colored import fg
from colored import stylize


@click.command()
def install():
    """
    args: None |
    Runs the install process on the host machine to configure it with ML libraries
    and any other dependencies

    """
    try:
        print(stylize("Launching the Vectordash installation process on this machine", fg("green")))
        print(stylize("When prompted with any questions, please hit ENTER for default values", fg("green")))

        # Path to install script and pip requirements file - should be in the current directory when this is executed
        install_script = os.path.expanduser('./install.sh')
        requirements = os.path.expanduser('./requirements.txt')

        # If either install script or requirements file is missing, exit the program
        if not os.path.isfile(install_script) or not os.path.isfile(requirements):
            print(stylize("You are missing one or more of the following files:", fg("red")))

            print(stylize(install_script, fg("red")))
            print(stylize(requirements, fg("red")))

            print("Only verified hosts can run this command")
            print("If you are a verified host, please go to https://vectordash.com/host to download the missing files")

            exit()

        else:
            try:
                # Run the installation script
                args = ['bash', install_script]
                subprocess.check_call(args)

            except subprocess.CalledProcessError:
                print("It looks as if your files have been corrupted. Please go to https://vectordash.com/host/ "
                      "to re-download the package and move the files to the appropriate directory: /var/vectordash/")

    except ValueError as e:
        print(stylize("The following error was encountered: ", fg("red")) + str(e))
        print(stylize("The Vectordash client could not be launched. Please make a github pull request with your error.",
                      fg("red")))
