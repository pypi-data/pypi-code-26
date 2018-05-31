from __future__ import absolute_import, division, print_function, unicode_literals


from Crypto.PublicKey import RSA

import os
import shutil
import subprocess
import sys
import getpass

from publisher import settings
from publisher.touchsurgery import TouchSurgery
from publisher.utils import WorkingDirectory, get_command_output, get_input, get_platform


def setup_users_machine():
    """
    User Setup for publish
        1. Check if git is installed
        2. Setup SSH
        3. Cloning the repo and git pull
    """
    if not git_installed():
        win_msg = 'Please install Github for windows from https://desktop.github.com/ before coming back and ' \
                  'continuing and running setup again.'
        mac_msg = 'Please install Git for Mac from https://git-scm.com/download/mac before running setup again.'

        print("%s" % mac_msg if 'darwin' in get_platform() else win_msg)
        sys.exit(1)

    print("Configuring ssh config file")
    check_and_create_directory(settings.SSH_DIRECTORY_PATH)
    check_and_create_file(settings.SSH_CONFIG_PATH)
    if not has_private_key():
        raise RuntimeError("Unable to proceed without a key. Please contact Hansel before trying again")
    configure_ssh_config()

    print('Configuring user profile')
    get_username()
    email = get_email()
    password = get_password()

    print('Generating key')
    sys.stdout.flush()
    pub_key = create_rsa_key_pair()
    login(email, password, pub_key)

    print("Installing and configuring git lfs")
    check_brew_installed()
    install_git_lfs()
    configure_git_lfs()

    check_and_create_directory(settings.GIT_DIRECTORY)

    print("Setting up the content repo")
    clone_content_repo()
    pull_content_repo()

    print("Setting up the channel repo")
    clone_channel_repo()
    pull_channel_repo()


def git_installed():
    try:
        subprocess.check_output(['git', '--version'])
    except OSError:
        print("Git not installed")
        return False
    return True


def get_username():
    print("Please enter your name here:")
    sys.stdout.flush()
    username = get_input()
    subprocess.check_output(['git', 'config', '--global', 'user.name', username])


def get_email():
    print("Please enter your touch surgery email here:")
    sys.stdout.flush()
    email = get_input()
    subprocess.check_output(['git', 'config', '--global', 'user.email', email])
    return email


def get_password():
    print("Please enter your touch surgery password here:")
    sys.stdout.flush()
    if get_platform().startswith('win'):
        print('Your password will not be hidden, so make sure you hide your screen while entering.')
        sys.stdout.flush()
        password = get_input()
    else:
        password = getpass.getpass()
    return password


def has_private_key():
    """Check whether the user has the correct private key
    """
    return os.path.exists(os.path.expanduser("~/.ssh/touchsurgery-studio.pem"))


def configure_ssh_config():
    """Creates and sets up an ssh config file, or appends the necessary entry to an existing one
    """
    shutil.copyfile(os.path.expanduser(settings.SSH_CONFIG_PATH), os.path.expanduser(settings.SSH_CONFIG_PATH + '.bak'))

    obsolete_stanza = (
        'Host studio-git.touchsurgery.com\n '
        'User ubuntu\n '
        'IdentitiesOnly true\n '
        'IdentityFile ~/.ssh/touchsurgery-studio.pem\n'
    )

    ssh_config_stanza = (
        'Host studio-git.touchsurgery.com\n'
        ' User git\n'
        ' IdentitiesOnly true\n'
        ' IdentityFile ' + settings.RSA_PRIVATE_KEY_PATH + '\n'
    )

    try:

        with open(os.path.expanduser(settings.SSH_CONFIG_PATH), "r") as config_file:
            current_config_text = config_file.read()
        ssh_config_missing = ssh_config_stanza not in current_config_text
        obsolete_stanza_present = obsolete_stanza in current_config_text

        # Remove outdated config info
        if obsolete_stanza_present:
            current_config_text = current_config_text.replace(obsolete_stanza, '')
            with open(os.path.expanduser(settings.SSH_CONFIG_PATH), "w") as config_file:
                config_file.write(current_config_text)

        # Add relevant config info
        if ssh_config_missing:
            with open(os.path.expanduser(settings.SSH_CONFIG_PATH), "a+") as config_file:
                config_file.write('\n' + '\n' + ssh_config_stanza)

    except Exception:
        print("Unable to configure the ssh config")
        raise


def check_brew_installed():
    """ Get Macs ready to brew
    """
    if 'darwin' in get_platform():
        output, _ = get_command_output(['brew', 'help'])
        if 'usage' not in output.lower():
            raise Exception("Please install Brew from here: https://brew.sh/")


def install_git_lfs():
    """Install git lfs
    """
    if 'darwin' in get_platform():
        output, _ = get_command_output(['which', 'git-lfs'])
        if 'usr' not in output.lower():
            call_command_and_print_exception(['brew', 'install', 'git-lfs'], "brew lfs install failure")

    call_command_and_print_exception(['git', 'lfs', 'install'], "lfs install failure")


def clone_content_repo():
    """Clone the content repo
    """
    if not os.path.exists(settings.PROCEDURE_CHECKOUT_DIRECTORY):
        try:
            with WorkingDirectory(settings.GIT_DIRECTORY):
                call_command_and_print_exception(['git', 'lfs', 'clone',
                                                  settings.PROCEDURE_REPOSITORY,
                                                  settings.PROCEDURE_CHECKOUT_DIRECTORY], "Clone repo failure")
        except Exception as e:
            print("Unable to clone the content repo")
            raise e
    else:
        print("Procedure repo already exists")


def pull_content_repo():
    """Run a git pull in the content repo
    """
    try:
        with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
            call_command_and_print_exception(['git', 'lfs', 'pull', 'origin', 'master'], "Git pull failure")
    except Exception as e:
        print("Unable to run a git pull in the content repo")
        raise e


def clone_channel_repo():
    """Clone the channel repo
    """
    if not os.path.exists(settings.CHANNELS_CHECKOUT_DIRECTORY):
        try:
            with WorkingDirectory(settings.GIT_DIRECTORY):
                call_command_and_print_exception(['git', 'lfs', 'clone',
                                                  settings.CHANNELS_REPOSITORY,
                                                  settings.CHANNELS_CHECKOUT_DIRECTORY], "Clone repo failure")
        except Exception as e:
            print("Unable to clone the content repo")
            raise e
    else:
        print("Channel repo already exists")


def pull_channel_repo():
    """Run a git pull in the channel repo
    """
    try:
        with WorkingDirectory(settings.CHANNELS_CHECKOUT_DIRECTORY):
            call_command_and_print_exception(['git', 'lfs', 'pull', 'origin', 'master'], "Git pull failure")
    except Exception as e:
        print("Unable to run a git pull in the channel repo")
        raise e


def call_command_and_print_exception(command, message):
    try:
        return subprocess.check_output(command)
    except Exception as e:
        print(message)
        raise e


def check_and_create_directory(path):
    try:
        if not os.path.exists(path):
            os.mkdir(path)
    except Exception:
        print("Could not find or create the directory")
        raise


def check_and_create_file(path):
    try:
        if not os.path.exists(path):
            subprocess.check_output(['touch', path])
    except Exception:
        print("Could not find or create the file")
        raise


def configure_git_lfs():
    """Set relevant  lfs settings
    """
    call_command_and_print_exception(['git', 'config', '--global', 'lfs.url',
                                      'https://live.touchsurgery.com/api/v3/lfs'], "lfs config failure")
    call_command_and_print_exception(['git', 'config', '--global', 'lfs.activitytimeout', '60'], "lfs config failure")


def create_rsa_key_pair():
    private_key = settings.RSA_PRIVATE_KEY_PATH
    public_key = settings.RSA_PUBLIC_KEY_PATH

    key = RSA.generate(2048)
    if os.path.exists(private_key):
        os.chmod(private_key, 0o0600)

    with open(private_key, 'wb') as rsa_pri:
        os.chmod(private_key, 0o0600)
        rsa_pri.write(key.exportKey('PEM'))

    pubkey = key.publickey()
    with open(public_key, 'wb') as rsa_pub:
        pub_key = pubkey.exportKey('OpenSSH')
        rsa_pub.write(pubkey.exportKey('OpenSSH'))

    return pub_key.split()[1]


def login(email, password, pub_key):
    """Verify TouchSurgery user here with rsa key and TouchSurgery login
    """
    login_instance = TouchSurgery()
    login_instance.login(email, password)
    login_instance.upload_key(pub_key)
