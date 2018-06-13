from abc import ABC, abstractmethod

from src.core.InstallOptions import InstallOptions
from src.core.Module import Module


class Store(ABC): # INIT: Download list

    @abstractmethod
    def __init__(self, options: InstallOptions):
        self.options = options

    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def add(self, path):
        pass

    @abstractmethod
    def update(self): # Download all modules
        pass

    @abstractmethod
    def getAll(self):
        pass

    @abstractmethod
    def print(self):
        pass

    @abstractmethod
    def remove(self, path):
        pass

    @abstractmethod
    def __getitem__(self, item) -> Module: # Even if not downloaded (update), give, error will be raise because modules.json will not contain it
        pass