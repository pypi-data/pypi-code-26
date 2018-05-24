import os, sys, stat
import string
import random

from shutil import copyfile, copy2


class RepoManager:

    MAX_FOLDERS = 1024
    MAX_DEPTH = 3
    MAX_FILES = 1024

    def __init__(self, root_folder, current_folder):

        self.ROOT_FOLDER = root_folder
        self.CURRENT_FOLDER = current_folder

        if current_folder==None:
            self.CURRENT_FOLDER = self.ROOT_FOLDER
    
        if not os.path.exists(self.CURRENT_FOLDER):
            os.makedirs(self.CURRENT_FOLDER)

    def get_absolute_uri(self, uri):
        return os.path.join(self.ROOT_FOLDER, uri)

    def create_folder(self, path):
        """
            Creates folder if it does not exist
        """
        if os.path.exists(path):
            s = "The folder's name: {} already exists.".format(path)
            raise ValueError(s)

        os.makedirs(path)

    def get_mock_path(self, path):
        """
            returns a mock destiny path
        """
        new_path = os.path.join(path, "files/")
        return new_path

    def get_destiny_path(self):
        """
            returns and available patch 
        """
        level, children, parent = self.set_initial()

        if children >= self.MAX_FOLDERS and parent == None:
            # The repository is full
            raise SystemError("The repository is full")

        #no esta entrando cuando ya existe el directorio
        elif children == 0 and level < self.MAX_DEPTH:
            # Can create folders 'cause it isn't in the deppest folder
            self.upgrade_current_folder(self.CURRENT_FOLDER)
            return self.get_destiny_path()
        else:
            # It's in the deppest folder
            files = self.get_files_count(self.CURRENT_FOLDER)
            if files < self.MAX_FILES:
                # It's available
                return self.CURRENT_FOLDER
            else:

                sibblings = self.get_folders_count(parent)
                if sibblings < self.MAX_FOLDERS:
                    # Current folder is not full
                    self.upgrade_current_folder(parent)
                    return self.CURRENT_FOLDER

                grand_parent = self.get_parent_folder(parent)
                if grand_parent != None:
                    self.upgrade_current_folder(grand_parent)
                    return self.get_destiny_path()

        return "files"

    def upgrade_current_folder(self, older_current):
        path = os.path.join(older_current, generate_name())
        self.create_folder(path)
        self.CURRENT_FOLDER = path

    def get_parent_folder(self, path):
        """
            Gets the parent folder, No1f path is root
        """
        parent = os.path.dirname(path)
        return parent if parent != '' else None

    def get_folder_level(self, path):
        parent = self.ROOT_FOLDER.split("/")
        x = path.split("/")
        return len(x) - len(parent)

    def get_files_count(self, path):
        files = 0
        for x in os.listdir(path):
            if os.path.isfile(os.path.join(path, x)):
                files += 1
        return files

    def get_folders_count(self, path):
        """
            Gets the count children of one level depth only
        """
        folders = 0
        for x in os.listdir(path):
            if os.path.isdir(os.path.join(path, x)):
                folders += 1

        return folders

    def set_initial(self):
        """
            Sets the inititial params
        """
        level = self.get_folder_level(self.CURRENT_FOLDER)
        children = self.get_folders_count(self.CURRENT_FOLDER)
        parent = self.get_parent_folder(self.CURRENT_FOLDER)
        return level, children, parent

    def extract_filename(self, path):
        return os.path.basename(path)


def generate_name(num=16):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(num))
