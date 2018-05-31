from concurrent.futures import ThreadPoolExecutor


class ServiceExecutor:
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if ServiceExecutor.__instance is None:
            ServiceExecutor()
        return ServiceExecutor.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if ServiceExecutor.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ServiceExecutor.__instance = self
            self.executor = ThreadPoolExecutor(max_workers=2)

    def submit(self, fn, *args, **kwargs):
        return self.executor.submit(fn, *args, **kwargs)

    def shutdown(self):
        self.executor.shutdown(True)
        ServiceExecutor.__instance = None
