from enum import IntFlag, auto


class Flag(IntFlag):
    """Represents a flag in a WHDLoad Slave.
    """
    Disk = auto()
    NoError = auto()
    EmulTrap = auto()
    NoDivZero = auto()
    Req68020 = auto()
    ReqAGA = auto()
    NoKbd = auto()
    EmulLineA = auto()
    EmulTrapV = auto()
    EmulChk = auto()
    EmulPriv = auto()
    EmulLineF = auto()
    ClearMem = auto()
    Examine = auto()
    EmulDivZero = auto()
    EmulIllegal = auto()

    def __str__(self):
        return self.name
