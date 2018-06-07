class StairsError(Exception):
    pass


class BadDatabaseError(StairsError):
    pass


class AlreadyEnteredError(StairsError):
    pass
