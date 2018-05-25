from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import input

import os
import subprocess
import sys
import shutil
import tempfile
import stat

from publisher import settings
from publisher.git_handling.history import get_commits_for_procedure, get_commits_for_phase
from publisher.git_handling.notes import clear_similar_historical_notes, edit_note
from publisher.git_handling.setup import call_command_and_print_exception
from publisher.utils import get_content_directories, WorkingDirectory, get_user_commit_selection, get_command_output, \
                            get_procedure_code, get_yes_no
from publisher.validators import validate_save


def build_procedure_list():

    """ Lists all current branches of the repository
    """

    def is_procedure(p):
        return p not in ['master', 'HEAD', '->'] and p.strip() != ''

    if os.path.exists(settings.PROCEDURE_CHECKOUT_DIRECTORY):
        with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
            subprocess.check_output(['git', 'fetch'])

            output, _ = get_command_output(['git', 'branch', '-r'])
            procedure_list = output.split()
            new_procedure_list = []
            for name in procedure_list:
                if 'origin' in name:
                    new_procedure_list.append(name.split('/')[-1])
                else:
                    new_procedure_list.append(name)

            return [p for p in new_procedure_list if is_procedure(p)]

    else:
        raise Exception('You do not have the content-production repository, please run the setup command.')


def display_procedures():
    print('\n'.join(build_procedure_list()))


def build_phase_list():
    """ Returns a list of phases for the current module
    """
    procedure_directories = get_content_directories(settings.PROCEDURE_CHECKOUT_DIRECTORY)
    if len(procedure_directories) == 0:
        return []

    phase_folder = os.path.join(settings.PROCEDURE_CHECKOUT_DIRECTORY, procedure_directories[0])
    return get_content_directories(phase_folder)


def get_user_selected_phase():
    phases = sorted(build_phase_list())
    return get_user_commit_selection('\nSelect a phase to display its history (0 to cancel)', phases)


def display_phase_history(phase):
    print("\n".join([str(c) for c in get_commits_for_phase(phase)]))


def revert_phase_commit(phase, commit_id):
    """ Get the phase folders state at a certain commit and copy it into the latest version of the branch, unsaved.
    """
    current_procedure = get_procedure_code()
    temp_phase_dir = tempfile.mkdtemp()
    phase_path = os.path.join(settings.PROCEDURE_CHECKOUT_DIRECTORY, current_procedure, phase)

    with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
        call_command_and_print_exception(['git', 'checkout', commit_id], 'Could not checkout specified commit.')
        shutil.copytree(phase_path, os.path.join(temp_phase_dir, phase))

        call_command_and_print_exception(['git', 'checkout', current_procedure], 'Could not revert to latest commit.')
        shutil.rmtree(phase_path, onerror=remove_readonly)

        shutil.copytree(os.path.join(temp_phase_dir, phase), os.path.join(current_procedure, phase))
        shutil.rmtree(temp_phase_dir, onerror=remove_readonly)


def display_phase_history_and_revert(phase_code):
    if not phase_code:
        sys.exit(0)
    with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
        output, _ = get_command_output(['git', 'status'])
        if 'working tree clean' in output:
            message = "\nEnter the number of the version you want to revert to (0 to cancel):"
            user_input = get_user_commit_selection(message, get_commits_for_phase(phase_code))
            if not user_input:
                sys.exit(0)
            revert_phase_commit(phase_code, user_input.id)
            print(phase_code + " has been reverted to the selected commit.")
        else:
            print('You have unsaved changes, please commit them or perform a tspub reset before reverting to a '
                  'different commit.')


def reset_repo():
    """ Git reset
    """
    with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
        call_command_and_print_exception(['git', 'reset', '--hard'], "Could perform git reset.")
        call_command_and_print_exception(['git', 'clean', '-f', '-d'], "Could perform git clean.")


def cl_reset_repo():
    """ Git reset with user interaction
    """
    print("Resetting will lose any unsaved changes, are you sure you wish to continue? (y or n):")
    sys.stdout.flush()
    reset_confirmation = get_yes_no()
    if reset_confirmation:
        reset_repo()
    else:
        print("Operation cancelled.")


def remove_readonly(func, path, _):
    """Clear the readonly bit and reattempt the removal
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)


def change_procedure(procedure):
    """Switches git branch to the procedure selected
    """

    with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
        command = ['git', '-c', 'filter.lfs.clean=', '-c', 'filter.lfs.smudge=', '-c', 'filter.lfs.process=', '-c',
                   'filter.lfs.required=false', 'checkout', procedure]
        message = 'Could not find the specified procedure. Make sure you have run setup and entered the correct ' \
                  'procedure name'
        call_command_and_print_exception(command, message)

        print("Retrieving procedure assets")
        subprocess.call(['git', '-c', 'filter.lfs.clean=', '-c', 'filter.lfs.smudge=', '-c', 'filter.lfs.process=',
                         '-c', 'filter.lfs.required=false', 'pull'])
        subprocess.call(['git', 'lfs', 'pull'])
        subprocess.call(['git', 'clean', '-xdf'])


def save_working_changes(message, initial=False, procedure_code=None):
    """Commits and pushes with the current changes to the repo
    """
    validate_save()

    try:
        with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
            if commit_working_changes(message):
                if initial:
                    subprocess.check_output(['git', 'push', '--set-upstream', 'origin', procedure_code])
                else:
                    pull_and_merge()
                    subprocess.check_output(['git', 'push'])
            else:
                print('No changes detected.')

    except subprocess.CalledProcessError:
        print('Could not commit/push the changes.')
        raise


def commit_working_changes(message):

    with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
        subprocess.check_output(['git', 'stage', '.'])
        output, _ = get_command_output(['git', 'commit', '-a', '-m', '"' + message + '"'])

    return 'nothing to commit' not in output


def publish(selected_commit):
    """ Publishes the procedure with a git note containing the distribution group to the chosen commit
    """

    all_commits = get_commits_for_procedure()
    with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):

        try:
            clear_similar_historical_notes(selected_commit, all_commits)
            edit_note(selected_commit)
        except Exception:
            print('Could not publish the procedure to the specified distribution group.')
            raise


def publish_with_display(dist_group, number_of_commits_shown):

    with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
        dist_group = dist_group or "TS-Testing"  # Default distribution group
        number_of_commits_shown = number_of_commits_shown or 10  # Default number of commits shown

        print("Current module:")
        print(subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']))

        all_commits = get_commits_for_procedure()
        if not all_commits:
            raise Exception("Either there were no previous commits or you set the optional '--number' argument to be "
                            "zero. Please either save your work first or input a positive integer to the --number "
                            "argument.")

        display_commits = all_commits[:int(number_of_commits_shown)]
        message = "\nEnter the number of the version you want to publish here (0 to cancel):"
        selected_commit = get_user_commit_selection(message, display_commits)

        if selected_commit:
            publish(selected_commit.copy_with_new_note(dist_group))


def delete_unstaged_changes():
    """Deletes all unstaged changes
    """
    try:
        with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
            subprocess.check_output(['git', 'checkout', '.'])
    except Exception:
        print("Could not delete local changes.")
        raise


def has_unstaged_changes():
    """Returns whether or not there are uncomitted changes
    """
    try:
        with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
            response = subprocess.check_output(['git', 'diff'])
            return True if len(response) else False
    except Exception:
        print("Could not retrieve the git diff. Please ensure the git repo is setup correctly")
        raise


def create_procedure_branch(procedure):
    """ Creates a new branch for the given procedure_code
    """
    try:
        with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
            subprocess.check_output(['git', 'checkout', 'master'])
            subprocess.check_output(['git', 'branch', procedure])
            change_procedure(procedure)
    except Exception:
        print("Unable to create a new procedure with name {}".format(procedure))
        raise


def pull_and_merge():
    """ Try a git pull and request user input to decide how a merge conflict is resolved if there is one
    """
    # Find the author of any potential merge conflicts
    try:
        subprocess.check_output(['git', 'pull'])
    except subprocess.CalledProcessError:
        # Ask the user which commit they would like to keep
        diff = subprocess.Popen(['git', 'diff'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(diff.communicate()[0])
        print("\n" + "There is a merge error.")
        print("Someone made a commit that conflicts with yours.")
        print("Would you like to accept your changes or theirs?")
        print("Type 'MINE' or 'THEIRS' to choose." + "\n")
        sys.stdout.flush()
        user_input = input()

        if user_input == "MINE":
            subprocess.check_output(['git', 'checkout', '--ours', '.'])
            subprocess.check_output(['git', 'add', '.'])
            subprocess.check_output(['git', 'commit', '-a', '-m', 'merge'])
        elif user_input == "THEIRS":
            subprocess.check_output(['git', 'checkout', '--theirs', '.'])
            subprocess.check_output(['git', 'add', '.'])
            subprocess.check_output(['git', 'commit', '-a', '-m', 'merge'])
        else:
            sys.exit(1)
