import logging
import os
import struct
from datetime import datetime
from typing import BinaryIO

from igamelister.amiga.chipset import Chipset
from igamelister.amiga.kickstart import Kickstart
from igamelister.amiga.slave_flag import Flag


class Slave(object):
    """Represents a WHDLoad Slave.
    """
    logger = logging.getLogger(__name__)

    def __hash__(self):
        return hash((self.installed_path,
                     self.file_path,
                     self.file_datetime.year,
                     self.file_datetime.month,
                     self.file_datetime.day,
                     self.file_size,
                     self.flags,
                     self.version,
                     self.base_mem_size,
                     self.exp_mem,
                     self.name,
                     self.copy,
                     self.info,
                     self.kickstarts,
                     self.kickstart_size,
                     self.configuration,
                     self.chipset))

    def __init__(self,
                 file: BinaryIO = None,
                 table: dict = None,
                 installed_path: str = None,
                 slave_id: int = None) -> None:
        """Initialize a new instance of the Slave class.

        :param file: A binary stream for a WHDLoad Slave file.
        :param table: A dictionary containing information about a single slave in the Install Package.
        :param installed_path: The path where the WHDLoad Slave is installed in.
        """
        if slave_id is not None:
            self.id = slave_id
        else:
            self.id = None

        if installed_path is not None:
            self.installed_path = installed_path
        else:
            self.installed_path = None

        self.file_path = None
        self.file_name = None
        self.file_datetime = None
        self.file_size = None
        self.version = None
        self._flags = 0
        self.base_mem_size = None
        self.exp_mem = None
        self._name = None
        self.copy = None
        self.info = None
        self._kickstarts = None
        self.kickstart_size = None
        self.configuration = None

        if table is not None and file is not None:
            raise ValueError("Expected either 'table' or 'file' argument, not both.")

        if table is not None:
            self.get_from_web(table)
        elif file is not None:
            self.get_from_file(file)

    @classmethod
    def from_file(cls, file: BinaryIO, installed_path: str = None, slave_id: int = None) -> 'Slave':
        """Initialize a new instance of the Slave class with data from
        a local WHDLoad Slave file.

        :param file: A binary stream for a WHDLoad Slave file.
        :param installed_path: The path where the WHDLoad Slave is installed in.
        :param slave_id: An ID number to assign to the Slave object.
        :return: A new instance of the Slave class.
        """
        return cls(file=file, installed_path=installed_path, slave_id=slave_id)

    @classmethod
    def from_web(cls, table: dict) -> 'Slave':
        """Initialize a new instance of the Slave class with data from
        an Install Package details page on the WHDLoad website
        (www.whdload.de).

        :param table: A dictionary of slave details from a WHDLoad Package
                      web page.
        :return: A new instance of the Slave class.
        """
        return cls(table=table)

    @property
    def name(self) -> str:
        return self._name if self._name is not None else ""

    @property
    def installed_dir(self) -> str:
        if self.installed_path is not None:
            return self.installed_path.replace(self.file_name, "")
        else:
            return ""

    @property
    def flags(self) -> tuple:
        """Gets the flags used by the WHDLoad Slave.

        :return: A list of flags.
        """
        result = []
        for flag in Flag:
            if self._flags & flag:
                result.append(flag)
        return tuple(result)

    @property
    def kickstarts(self) -> tuple:
        """Gets the Kickstart ROMs used by the WHDLoad Slave.

        :return: A tuple of Kickstart ROMs
        """
        if self._kickstarts is None:
            return ()
        return tuple(self._kickstarts)

    @property
    def chipset(self) -> tuple:
        """Gets Amiga chipset types required for the WHDLoad Slave.

        :return: A set of Amiga chipsets.
        """
        chipset = set()
        if self.file_name is not None or self._name is not None or self.info is not None:
            if "AGA" in self.file_name or "AGA" in self._name or "AGA" in self.info:
                chipset.add(Chipset.AGA)
            if "ECS" in self.file_name or "ECS" in self._name or "ECS" in self.info:
                chipset.add(Chipset.ECS)
            if "OCS" in self.file_name or "OCS" in self._name or "OCS" in self.info:
                chipset.add(Chipset.OCS)
            if "Arcadia" in self.file_name or "Arcadia" in self._name or "Arcadia" in self.info:
                chipset.add(Chipset.Arcadia)
            if "CD32" in self.file_name or "CD32" in self._name or "CD32" in self.info:
                chipset.add(Chipset.CD32)
            if "CD³²" in self.file_name or "CD³²" in self._name or "CD³²" in self.info:
                chipset.add(Chipset.CD32)
            if "CDTV" in self.file_name or "CDTV" in self._name or "CDTV" in self.info:
                chipset.add(Chipset.CDTV)
            if "AmigaCD" in self.file_name or "AmigaCD" in self._name or "AmigaCD" in self.info:
                chipset.add(Chipset.AmigaCD)
            if len(chipset) == 0:
                chipset.add(Chipset.OCS)
                chipset.add(Chipset.ECS)
        return tuple(chipset)

    def get_from_web(self, table: dict):
        """Get information an Install Package details page on the
        WHDLoad website (www.whdload.de)

        :param table: A dictionary containing information about
                      a single slave in the Install Package.
        """
        self.file_name = table["file_name"]
        self.file_datetime = table["file_datetime"]
        self.file_size = table["file_size_bytes"]
        self.version = table["slave_version"]
        flags = table["slave_flags"]
        if len(flags) > 0:
            for flag in flags:
                if flag == "Disk":
                    self._flags = int(self._flags | Flag.Disk)
                elif flag == "NoError":
                    self._flags = int(self._flags | Flag.NoError)
                elif flag == "EmulTrap":
                    self._flags = int(self._flags | Flag.EmulTrap)
                elif flag == "NoDivZero":
                    self._flags = int(self._flags | Flag.NoDivZero)
                elif flag == "Req68020":
                    self._flags = int(self._flags | Flag.Req68020)
                elif flag == "ReqAGA":
                    self._flags = int(self._flags | Flag.ReqAGA)
                elif flag == "NoKbd":
                    self._flags = int(self._flags | Flag.NoKbd)
                elif flag == "EmulLineA":
                    self._flags = int(self._flags | Flag.EmulLineA)
                elif flag == "EmulTrapV":
                    self._flags = int(self._flags | Flag.EmulTrapV)
                elif flag == "EmulChk":
                    self._flags = int(self._flags | Flag.EmulChk)
                elif flag == "EmulPriv":
                    self._flags = int(self._flags | Flag.EmulPriv)
                elif flag == "EmulLineF":
                    self._flags = int(self._flags | Flag.EmulLineF)
                elif flag == "ClearMem":
                    self._flags = int(self._flags | Flag.ClearMem)
                elif flag == "Examine":
                    self._flags = int(self._flags | Flag.Examine)
                elif flag == "EmulDivZero":
                    self._flags = int(self._flags | Flag.EmulDivZero)
                elif flag == "EmulIllegal":
                    self._flags = int(self._flags | Flag.EmulIllegal)
                else:
                    raise ValueError(f"Unexpected flag ({flag}) found in web data.")
        else:
            self._flags = 0

        self.base_mem_size = table["slave_chip_mem"]
        self.exp_mem = table["slave_exp_mem"]
        self._name = table["slave_name"]
        self.info = table["slave_info"]
        self.copy = table["slave_copy"]
        kickstart_names = table["slave_kickstart_names"]
        kickstart_checksums = table["slave_kickstart_checksums"]
        self.kickstart_size = table["slave_kickstart_size_bytes"]
        self.configuration = table["slave_configuration"]

        if len(kickstart_names) > 0 and len(kickstart_checksums) > 0:
            if len(kickstart_names) == len(kickstart_checksums):
                self._kickstarts = []
                for i in range(len(kickstart_names)):
                    self._add_kickstart(kickstart_names[i], int(kickstart_checksums[i].replace("$", ""), 16))

    def get_from_file(self, file: BinaryIO):
        """Get information from a local WHDLoad Slave file.

        :param file: A binary stream for a local WHDLoad Slave file.
        """
        start_offset = 32
        security_length = 4

        self.file_path = file.name
        self.file_name = os.path.basename(self.file_path)
        self.file_size = os.stat(self.file_path).st_size
        self.file_datetime = datetime.fromtimestamp(os.stat(self.file_path).st_mtime)

        with file:
            file.seek(start_offset + security_length)
            slave_id, \
                version, \
                flags, \
                base_mem_size, \
                exec_install = struct.unpack(">8sHHLL", file.read(20))

            if not slave_id == b'WHDLOADS':  # or not exec_install == 0:
                raise IOError(f"Invalid WHDLoad header in file '{self.file_name}'.")

            self.version = version
            self._flags = flags
            self.base_mem_size = base_mem_size

            # skip gameloader_ptr, currentdir_ptr, dontcache_ptr,
            file.seek(6, 1)

            if version < 4:
                return

            # skip key_debug, key_exit
            file.seek(2, 1)

            if version < 8:
                return

            self.exp_mem = int.from_bytes(file.read(4), byteorder='big', signed=False)

            if version < 10:
                return

            name_ptr, \
                copy_ptr, \
                info_ptr = struct.unpack(">HHH", file.read(6))

            self._name = self._get_string_from_file(file, name_ptr)
            self.copy = self._get_string_from_file(file, copy_ptr)
            self.info = self._get_string_from_file(file, info_ptr)

            if version < 16:
                return

            self._kickstarts = []

            kick_name_ptr, \
                kick_size, \
                kick_crc = struct.unpack(">HLH", file.read(8))

            self.kickstart_size = kick_size
            if kick_crc == 65535:
                self._add_kickstarts_from_file(file, kick_name_ptr)
            elif kick_crc == 0:
                self._add_kickstart(kick_name_ptr, kick_crc)
            else:
                self._add_kickstart(self._get_string_from_file(file, kick_name_ptr), kick_crc)

            if self.version < 17:
                return

            config_ptr = int.from_bytes(file.read(2), byteorder='big', signed=False)
            self.configuration = self._get_string_from_file(file, config_ptr)

    @classmethod
    def _get_string_from_file(cls, slave: BinaryIO, ptr: int) -> str:
        """Get a string from the Slave file binary stream.
        The string is terminated when the next byte equals 0x00.

        :param slave: The WHDLoad Slave file binary stream.
        :param ptr: Address pointer to beginning of string.
        :return: The requested string.
        """
        start_offset = 32

        last_pos = slave.tell()
        result = ""
        byte = None
        slave.seek(start_offset + ptr)
        while byte != b'\x00':
            if byte:
                if byte == b'\xff':
                    result += "\n"
                else:
                    result += byte.decode('latin1')
            byte = slave.read(1)
        slave.seek(last_pos)
        return result

    def _add_kickstart(self, name: str, checksum: int):
        """Add a Kickstart ROM to the Slave.

        :param name: The name of the Kickstart ROM.
        :param checksum: The checksum (CRC16) of the Kickstart ROM.
        """
        self._kickstarts.append(Kickstart(name, checksum))

    def _add_kickstarts_from_file(self, slave: BinaryIO, ptr: int):
        """Add Kickstart ROMs to the kickstarts class property.

        :param slave: The WHDLoad Slave file binary stream.
        :param ptr: Address pointer to the beginning of the Kickstart
                    ROM table in the WHDLoad Slave file.
        """
        start_offset = 32

        last_pos = slave.tell()
        slave.seek(start_offset + ptr)
        current_ptr = None
        while True:
            if current_ptr:
                slave.seek(current_ptr)
            kick_crc, kick_name_ptr = struct.unpack(">HH", slave.read(4))
            if kick_crc == 0:
                break
            current_ptr = slave.tell()
            kick_name = self._get_string_from_file(slave, kick_name_ptr)
            self._add_kickstart(kick_name, kick_crc)
        slave.seek(last_pos)
