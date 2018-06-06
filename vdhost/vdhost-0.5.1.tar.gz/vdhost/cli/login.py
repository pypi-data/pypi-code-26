import click
import os
import json
import requests

from colored import fg
from colored import stylize

from vdhost import VECTORDASH_URL


@click.command(name='login')
def login():
    """
    args: none |
    Allows host to login on machine to be hosted

    """
    try:
        # Path to vectordash directory
        var_folder = os.path.expanduser('/var/')
        var_vd_folder = os.path.expanduser(var_folder + 'vectordash/')

        # If the var directory does not exist, create it
        if not os.path.isdir(var_folder):
            os.mkdir(var_folder)

        # If the vectordash directory does not exist, create it
        if not os.path.isdir(var_vd_folder):
            os.mkdir(var_vd_folder)

        # Save ids to gpu_ids file
        login_file = var_vd_folder + 'login.json'

        # Ask user for email address
        email = input(stylize("Email: ", fg("blue")))

        # Ask user for machine key
        machine_key = input(stylize("Machine key: ", fg("blue")))

        r = requests.post(VECTORDASH_URL + "authenticate-host/",
                          data={'email': email, 'machine_key': machine_key})
        resp = r.text
        resp = json.loads(resp)
        if not resp['valid_authentication']:
            print("You do not have valid authentication. Did you run 'vdhost login'?")
            exit(0)
        else:
            # Securely save data
            with open(login_file, 'w') as f:
                data = {'email': email, 'machine_key': machine_key}
                json.dump(data, f)

            print(stylize("Saved login information", fg("green")))
            print("If you have already ran " + stylize("vdhost install", fg("blue")) +
                  " successfully, you can now list your machine on Vectordash by running " +
                  stylize("vdhost start-hosting", fg("blue")))
    except PermissionError:
        print("A Permission Denied Error was encountered. Try executing the command again as such: " + stylize("sudo vdhost login", fg("blue")))
    except Exception as e:
        print(stylize("The following error was encountered: ", fg("red")) + str(e))
