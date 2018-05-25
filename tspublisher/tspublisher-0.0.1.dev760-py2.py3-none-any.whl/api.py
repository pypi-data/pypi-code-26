from __future__ import absolute_import, division, print_function, unicode_literals

from publisher.procedure_content import build_procedure_list, build_phase_list, has_unstaged_changes, cl_reset_repo, \
    change_procedure, save_working_changes, get_commits_for_procedure, publish, create_procedure_branch
from publisher.utils import get_procedure_code
from publisher.processing.procedure import build_single_phase, build_procedure, create_procedure


class Publisher(object):
    def __init__(self):
        self.procedure_code = get_procedure_code()

    def get_procedure_list(self):
        return build_procedure_list()

    def get_phase_list(self):
        return build_phase_list()

    def set_current_procedure(self, proc_code):
        self.procedure_code = proc_code

    def workon_procedure(self, proc_code):
        self.check_unstaged_changes()
        change_procedure(proc_code)
        self.set_current_procedure(proc_code)

    def check_unstaged_changes(self):
        if has_unstaged_changes():
            raise UnsavedChangesError("Unsaved changes found, please contact pipeline.")

    def reset_repo(self):
        cl_reset_repo()

    def publish(self, message, distribution_group):
        save_working_changes(message)
        selected_commit = get_commits_for_procedure()[-1]
        publish(selected_commit.copy_with_new_note(distribution_group))

    def update_phase(self, phase_code, graphics, pip_graphics, widget_graphics, thumbnails, step_numbers, info_step,
                     country_restrict):
        build_single_phase(phase_code, graphics=graphics, pip_graphics=pip_graphics, widget_graphics=widget_graphics,
                           thumbnails=thumbnails, step_numbers=step_numbers, info_step=info_step,
                           country_restriction=country_restrict)

    def update_procedure(self, graphics, pip_graphics, widget_graphics, thumbnails, step_numbers, info_step,
                         country_restrict):
        build_procedure(self.procedure_code, build_phases=True, graphics=graphics, pip_graphics=pip_graphics,
                        widget_graphics=widget_graphics, thumbnails=thumbnails, step_numbers=step_numbers,
                        info_step=info_step, country_restriction=country_restrict)

    def update_procedure_info(self, thumbnails):
        build_procedure(self.procedure_code, build_phases=False, graphics=False, pip_graphics=False,
                        widget_graphics=False, thumbnails=thumbnails, step_numbers=False, info_step=False,
                        country_restriction="")

    def create_procedure(self, proc_code):
        if proc_code not in build_procedure_list():
            self.check_unstaged_changes()
            create_procedure_branch(proc_code)
        else:
            raise ProcedureExistsError("The procedure {0} already exists and thus cannot be created".format(proc_code))

        create_procedure(proc_code)

        save_working_changes("Initial commit", initial=True, procedure_code=proc_code)


class UnsavedChangesError(IOError):
    pass


class ProcedureExistsError(IOError):
    pass
