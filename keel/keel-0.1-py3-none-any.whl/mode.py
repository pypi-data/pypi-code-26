import util_ps
from psutil import NoSuchProcess


# base class
class Mode(object):
    def __init__(self, user):
        self.user = user

    def change_user(self, user):
        self.user = user

    # by default, will list all processes that are owned by the specified user
    def get_processes(self):
        return util_ps.get_proc_by_username(self.user)

    def get_title(self):
        return "Choose a process to kill and hit enter"

    def kill_process(self, pid):
        try:
            util_ps.kill_pid(pid)
            return True  # true for killed. may be reworked
        except (NoSuchProcess, TypeError, RuntimeError, OverflowError) as e:
            return e

    # for when you need all the damn proccesses irregardless of user
    def get_all_processes(self):
        return util_ps.get_all_proc()

    def __str__(self):
        return "Regular"

#
# # for when the user wants to switch to the mode with all processes
# class AllProcessesMode(Mode):
#     def get_processes(self):
#         return util_ps.get_all_proc()


# for when the user wants to switch to the mode with open network connections
class OpenConnectionsMode(Mode):
    def __init__(self, user):
        super().__init__(user)
        self.kind = 'inet'  # todo: see about reworking this

    def change_kind(self, kind):
        self.kind = kind

    def get_title(self):
        return "Choose a connection to close and hit enter"

    def get_processes(self):
        return util_ps.get_open_con(self.kind)

    def get_types(self):
        return 'inet', 'inet4', 'inet6', 'tcp', 'tcp4', 'tcp6', 'udp', 'udp4', 'udp4', 'udp6', 'unix', 'all'

    def __str__(self):
        return "Connections"

# for when the user wants to monitor the processes for a specific user
# class UserProcessesMode(Mode):
    # def __init__(self, user):
    #     super().__init__(user)
    #     self.user = user

    # def change_user(self, user):
    #     self.user = user
