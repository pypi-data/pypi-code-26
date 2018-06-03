class Kickstart:
    """Represents a Kickstart ROM used by a WHDLoad Slave.
    """
    name = None
    checksum = None

    def __init__(self, name: str, checksum: int) -> None:
        """Initialize a new instance of the Kickstart class.

        :param name: The name of the Kickstart ROM.
        :param checksum: The checksum (CRC16) of the Kickstart ROM.
        """
        self.name = name
        self.checksum = checksum

    def __hash__(self):
        return hash((self.name, self.checksum))

    def __str__(self):
        return f"{self.name} ({hex(self.checksum)})"
