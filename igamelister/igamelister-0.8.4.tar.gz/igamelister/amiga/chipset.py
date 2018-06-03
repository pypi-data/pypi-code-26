from enum import Enum, auto


class Chipset(Enum):
    OCS = auto()
    ECS = auto()
    AGA = auto()
    CD32 = auto()
    AmigaCD = auto()
    CDTV = auto()
    Arcadia = auto()
    Unknown = auto()

    def __str__(self):
        return self.name
