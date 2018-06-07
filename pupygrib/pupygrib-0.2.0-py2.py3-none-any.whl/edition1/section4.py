"""Binary data sections of GRIB edition 1."""

from __future__ import unicode_literals

import numpy

from pupygrib import base
from pupygrib import fields
from pupygrib.edition1.fields import FloatField


class BinaryDataSection(base.Section):

    """The binary data section (4) of an edition 1 GRIB message."""

    section4Length = fields.Uint24Field(1)
    dataFlag = fields.Uint8Field(4)
    binaryScaleFactor = fields.Int16Field(5)
    referenceValue = fields.BytesField(7, 4)
    bitsPerValue = fields.Uint8Field(11)
    values = fields.BytesField(12)

    def _unpack_values(self):
        raise NotImplementedError(
            "pupygrib does not support the current packing"
        )


class SimpleGridDataField(base.Field):

    """Simply packed grid-point data values."""

    def get_value(self, section, offset):
        bits_per_value = section.bitsPerValue
        if bits_per_value == 0:
            return None
        if bits_per_value % 8 != 0:
            raise NotImplementedError(
                "pupygrib does not support fractional bytes per value "
                "(bitsPerValue is {})".format(bits_per_value)
            )

        unused_bytes = -(section.dataFlag & 0x0f) // 8 or None
        dtype = numpy.dtype('>u{}'.format(bits_per_value // 8))
        buf = section._data[offset:unused_bytes]
        try:
            return numpy.frombuffer(buf, dtype=dtype)
        except AttributeError:
            # In Python 2 we're forced to do an unneccesary copy with
            # memoryview.tobytes() to get an old-style buffer since:
            #
            # * numpy.frombuffer() only accept old-style buffers
            #   (which is the reason we're in this except clause).
            #
            # * We can't convert a memoryview to an old-style buffer
            # * with buffer().
            #
            # * We can't globaly use old-style buffer objects since
            # * they don't support slicing.
            #
            # * We can't use numpy.array() because it ignores the
            #   dtype in favor of memoryview.format (which will always
            #   be 'B') and a memoryview can't be cast to another
            #   format in Python 2.
            return numpy.frombuffer(buf.tobytes(), dtype=dtype)


class SimpleGridDataSection(BinaryDataSection):

    """A simply packed grid-point data section (4) of GRIB edition 1."""

    referenceValue = FloatField(7)
    values = SimpleGridDataField(12)

    def _unpack_values(self):
        values = 0 if self.values is None else self.values
        return self.referenceValue + values * 2**self.binaryScaleFactor


def get_section(buf, offset, length):
    """Return a new section 4 of the correct type from *buf* at *offset*."""
    datadesc = BinaryDataSection(buf, offset, length)
    try:
        sectionclass = {
            0x00: SimpleGridDataSection,
        }[datadesc.dataFlag & 0xf0]
    except KeyError:
        return datadesc
    else:
        return sectionclass(buf, offset, length)
