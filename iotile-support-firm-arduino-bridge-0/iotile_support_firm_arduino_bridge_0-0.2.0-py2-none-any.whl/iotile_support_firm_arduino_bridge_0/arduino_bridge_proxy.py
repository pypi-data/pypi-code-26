from iotile.core.hw.proxy.proxy import TileBusProxyObject
from iotile.core.hw.exceptions import *
from iotile.core.utilities.console import ProgressBar
import struct
from iotile.core.utilities.intelhex import IntelHex
from time import sleep
from iotile.core.utilities.typedargs.annotate import annotated,param,return_type, context
from iotile.core.utilities.typedargs import iprint
from iotile.core.utilities import typedargs
from itertools import product
from iotile.core.exceptions import *
import math

@context("ArduinoBridge")
class ArduinoBridge(TileBusProxyObject):
    """
    Provide access to GPIO tile functionality


    :param stream: CMDStream instance that can communicate with this tile
    :param addr: Local tilebus address of this tile
    """

    @classmethod
    def ModuleName(cls):
        return 'ardbrg'

    def __init__(self, stream, addr):
        super(ArduinoBridge, self).__init__(stream, addr)

    @return_type("map(string, integer)")
    def last_event(self):
        """Get the last sample received from the arduino."""

        sample, stream = self.rpc(0x80, 0x00, result_format="LH")

        return {'stream': stream, 'value': sample}

    @param("event", "integer", desc="The event number to send to the arduino (in [0-9] inclusive)")
    def send_event(self, event):
        """Send an event to Arduino.

        There are 10 supported events, numbered 0 - 9.  You can
        send any one passing the appropriate event number.

        TODO:
            Currently only two events are supported because of possible serial value
            corruption.
        """

        if event < 0 or event > 9:
            raise ArgumentError("Invalid event number (must be in [0, 9])", event=event)

        self.rpc(0x81, event)
        
    @param("byte", "integer", desc="The integer representation of the byte you want to send to the arduino. [0-255] inclusive")
    def send_raw(self, byte):
        """Send and envent to the Arduino.

        same as send_event, but for all values in the 0-255 inclusive range.
        """

        if byte < 0 or byte > 255:
            raise ArgumentError("Invalid value (must be in [0,255] inclusive)")

        self.rpc(0x8F, 0xFF, byte, arg_format="B")
