import click
import subprocess
import os

from colored import fg
from colored import stylize


@click.command(name='stop-hosting')
def stop_hosting():
    """
    args: None |
    Stops the Vectordash client daemon on the host's machine

    """
    try:
        print(stylize("Stopping the Vectordash client on this machine", fg("green")))

        # Path to vectordash directory
        var_folder = os.path.expanduser('/var/')
        var_vd_folder = os.path.expanduser(var_folder + 'vectordash/')
       
        if not os.path.isfile(var_vd_folder + 'install_complete'):
            print(stylize("Please run 'vdhost install' first!", fg("red")))
            return

        # If directories don't exist, exit the program and instruct user to run 'vdhost install'
        if not os.path.isdir(var_folder) or not os.path.isdir(var_vd_folder):
            print(stylize("Could not exit the program", fg("red")))
            print(stylize("Are you sure have run:", fg("red")), stylize("vdhost install", fg("blue")))
            print(stylize("If not, please navigate to the vectordash-host package directory and run that command",
                          fg("red")))
            return

        if not os.path.isfile("/etc/supervisor/conf.d/vdclient.conf"):
            print(stylize("Something went wrong during the install. Please try running 'vdhost install' again."))
            return

        # File for checking if the client is running or not
        client_running_file = os.path.expanduser(var_vd_folder + 'client_running')

        # If the client pid file exists, stop the client
        if os.path.exists(client_running_file):

            # Read in pid (number)
            print("Checking if the client hosting process is running...")
            f = open(client_running_file, 'r')
            p = f.read()
            f.close()

            # If the pid is below 0, then it is currently not running
            if int(p) == -1:
                print("You are not currently running the client hosting process. Run " +
                      stylize("vdhost start-hosting", fg("blue")) + " to start hosting on Vectordash")
                return

            subprocess.call("sudo supervisorctl stop vdclient", shell=True)

            # kill the process with process id pid
            #args = ['kill', '--', '-$(ps', '-o', 'pgid=', p, '|', 'grep', '-o', '[0-9]*)']
            #subprocess.check_call(args)

            # If the pids have not yet been killed, try again
            #while pid_exists(p):
            #    print("Attempting to force stop the client process")
            #    args2 = ['kill', '-9', '-p', p]
            #    subprocess.check_call(args2)

            # write -1 to pid file (indicating the hosting has stopped)
            f = open(client_running_file, 'w')
            f.write("-1")
            f.close()

        else:
            print("Could not check the client_running file for process id. Did you ever start the client process?")
            return

    except ValueError as e:
        print(stylize("The following error was encountered: ", fg("red")) + str(e))

def pid_exists(pid):
    """
    Check whether pid exists in the current process table.
    """
    try:
        print("Double-checking to ensure client hosting was stopped")
        os.kill(int(pid), 0)
    except OSError:
        print("Pid: " + pid + " killed")
        return False
    else:
        print("Pid: " + pid + " still exists")
        return True
