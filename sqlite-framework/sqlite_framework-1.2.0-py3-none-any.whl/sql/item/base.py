class SqlItem:
    def __init__(self):
        # the only purpose of this constructor is to hint IDE to always call super on subclasses
        # to properly support multiple inheritance
        super().__init__()

    def str(self):
        raise NotImplementedError()


class StringItem(SqlItem):
    def __init__(self, string: str):
        super().__init__()
        self.string = string

    def str(self):
        return self.string


class NamedItem(StringItem):
    def __init__(self, name: str):
        super().__init__(name)
