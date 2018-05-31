
class Catalog(dict):
    def register(self, command, name=None):
        if not name:
            name = command.name
        if name in self:
            raise KeyError('Command already registered')
        self[name] = command
        return command


catalog = Catalog()
