from abc import ABC, abstractmethod


class Driver(ABC):

    @abstractmethod
    async def find_by(self, **kwargs):
        pass

    @abstractmethod
    async def find_by_id(self, id):
        pass

    @abstractmethod
    async def remove(self, doc):
        pass

    @abstractmethod
    async def update(self, doc):
        pass

    @abstractmethod
    async def save(self, doc):
        pass