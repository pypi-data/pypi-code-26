# -*- coding: utf-8 -*-

import struct
import sys
import base64
import json
import dateutil.parser
import datetime

class UnsupportedFileVersionException(Exception):
    def __init__(self, v):
        self.file_version = v

    def __str__(self):
        return str(self.file_version)

class Utility:
    @staticmethod
    def to_none_or_base64_encoded_string(s):
        if s is None:
            return None
        else:
            return base64.b64encode(s).decode("utf-8")
    @staticmethod
    def to_none_if_none_else_to_dict(v):
        if v is None:
            return None
        else:
            return v.to_dict();
    @staticmethod
    def to_none_or_unicode_decoded_string(s):
        if s is None:
            return None
        else:
            if sys.version_info >= (3, 0):
                return s
            else:
                return s.decode("utf-8")

    @staticmethod
    def none_if_not_exists_else_value(m, k):
        return None if k not in m else m[k]

    @staticmethod
    def none_if_not_exists_else_base64decoded_value(m, k):
        return None if k not in m else base64.b64decode(m[k])

    @staticmethod
    def byte_to_int(v):
        #Byte -> int conversion is handled differently in python 2 vs 3
        if sys.version_info >= (3, 0):
            return int.from_bytes(v, byteorder='little')
        else:
            return int("".join(reversed(v)).encode('hex'), 16)
        
class ATCInfoBlock:
    def __init__(self, dr, rUUID, pUDID, pm, rs, rh, l):
        assert(dr is None or len(dr) <= 32)
        assert(rUUID is None or len(rUUID) <= 40)
        assert(pUDID is None or len(pUDID) <= 44)
        assert(pm is None or len(pm) <= 32)
        assert(rs is None or len(rs) <= 32)
        assert(rh is None or len(rh) <= 32)
        assert(l is None or len(l) <= 52)

        self.date_recorded = dr
        self.recording_UUID = rUUID
        self.phone_UDID = pUDID
        self.phone_model = pm
        self.recorder_software = rs
        self.recorder_hardware = rh
        self.location = l

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(self, other.__class__):
            return self.date_recorded == other.date_recorded \
                    and self.recording_UUID == other.recording_UUID \
                    and self.phone_UDID == other.phone_UDID \
                    and self.phone_model == other.phone_model \
                    and self.recorder_software == other.recorder_software \
                    and self.recorder_hardware == other.recorder_hardware \
                    and self.location == other.location
        return False

    def to_dict(self):
        d = {}
        d["date_recorded"] = Utility.to_none_or_unicode_decoded_string(self.date_recorded)
        d["recording_UUID"] = Utility.to_none_or_unicode_decoded_string(self.recording_UUID)
        d["phone_UDID"] = Utility.to_none_or_unicode_decoded_string(self.phone_UDID)
        d["phone_model"] = Utility.to_none_or_unicode_decoded_string(self.phone_model)
        d["recorder_software"] = Utility.to_none_or_unicode_decoded_string(self.recorder_software)
        d["recorder_hardware"] = Utility.to_none_or_unicode_decoded_string(self.recorder_hardware)
        d["location"] = Utility.to_none_or_unicode_decoded_string(self.location)
        return d

    @staticmethod
    def from_json(js):
        dr = Utility.none_if_not_exists_else_value(js, "date_recorded")
        rUUID = Utility.none_if_not_exists_else_value(js, "recording_UUID")
        pUDID = Utility.none_if_not_exists_else_value(js, "phone_UDID")
        pm = Utility.none_if_not_exists_else_value(js, "phone_model")
        rs = Utility.none_if_not_exists_else_value(js, "recorder_software")
        rh = Utility.none_if_not_exists_else_value(js, "recorder_hardware")
        l = Utility.none_if_not_exists_else_value(js, "location")
        return ATCInfoBlock(dr, rUUID, pUDID, pm, rs, rh, l)

class ATCFormatBlock:
    def __init__(self, ff, freq, res, flags, reserved):
        assert(ff is None or len(ff) == 1)
        assert(freq is None or freq >= 0 and freq <= 65535)
        assert(res is None or res >= 0 and res <= 65535)
        assert(flags is None or len(flags) == 1)
        assert(reserved is None or reserved >= 0 and reserved <= 65535)
        self.fmt_format = ff
        self.frequency = freq
        self.resolution = res
        self.flags = flags
        self.reserved = reserved

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(self, other.__class__):
            return self.fmt_format == other.fmt_format \
                    and self.frequency == other.frequency \
                    and self.resolution == other.resolution \
                    and self.flags == other.flags \
                    and self.reserved == other.reserved
        return False

    @staticmethod
    def from_json(js):
        ff = Utility.none_if_not_exists_else_base64decoded_value(js, "fmt_format")
        freq = Utility.none_if_not_exists_else_value(js, "frequency")
        res = Utility.none_if_not_exists_else_value(js, "resolution")
        flags = Utility.none_if_not_exists_else_base64decoded_value(js, "flags")
        reserved = Utility.none_if_not_exists_else_value(js, "reserved")
        return ATCFormatBlock(ff, freq, res, flags, reserved)

    def to_dict(self):
        d = {}
        d["fmt_format"] = Utility.to_none_or_base64_encoded_string(self.fmt_format)
        d["frequency"] = self.frequency
        d["resolution"] = self.resolution
        d["flags"] = Utility.to_none_or_base64_encoded_string(self.flags)
        d["reserved"] = self.reserved
        return d

class PyATC:
    __file_version = None
    __format_block = None
    __info_block = None
    __lead1_ecg_block = None
    __lead2_ecg_block = None
    __ann_block = None

    #Constants
    file_header = (65, 76, 73, 86, 69, 0, 0, 0)
    file_version_key = "file_version"
    format_block_key = "format_block"
    info_block_key = "info_block"
    ann_block_key = "ann_block"
    samples_key = "samples"
    lead1_key = "lead1"
    lead2_key = "lead2"


    def __init__(self, fv, fb, ib, l1eb, l2eb, ab):
        self.__file_version = fv
        self.__format_block = fb
        self.__info_block = ib
        self.__lead1_ecg_block = l1eb
        self.__lead2_ecg_block = l2eb
        self.__ann_block = ab

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(self, other.__class__):
            return self.__file_version == other.__file_version \
                    and self.__format_block == other.__format_block \
                    and self.__info_block == other.__info_block \
                    and self.__lead1_ecg_block == other.__lead1_ecg_block \
                    and self.__lead2_ecg_block == other.__lead2_ecg_block \
                    and self.__ann_block == other.__ann_block
        return False

    def get_lead1_samples(self):
        return self.__lead1_ecg_block

    def get_lead2_samples(self):
        return self.__lead2_ecg_block

    def get_recording_duration(self):
        return len(self.__lead1_ecg_block) / self.__format_block.frequency

    @staticmethod
    def from_json(js):
        file_version = None
        format_block = None
        info_block = None
        lead1_ecg = None
        lead2_ecg = None
        ann_block = None

        if PyATC.file_version_key in js:
            file_version = tuple(js[PyATC.file_version_key])
        if PyATC.format_block_key in js:
            format_block = ATCFormatBlock.from_json(js[PyATC.format_block_key])
        if PyATC.info_block_key in js:
            info_block = ATCInfoBlock.from_json(js[PyATC.info_block_key])
        if PyATC.samples_key in js:
            if PyATC.lead1_key in js[PyATC.samples_key]:
                lead1_ecg = js[PyATC.samples_key][PyATC.lead1_key]
            if PyATC.lead2_key in js[PyATC.samples_key]:
                lead2_ecg = js[PyATC.samples_key][PyATC.lead2_key]
        if PyATC.ann_block_key in js:
            ann_block = base64.b64decode(js[PyATC.ann_block_key])

        return PyATC(file_version, format_block, info_block, lead1_ecg, lead2_ecg, ann_block)

    @staticmethod
    def read_json_file(path):
        with open(path, "r") as f:
            return PyATC.from_json(json.loads(f.read()))

    def to_json(self):
        samples = {}
        samples[PyATC.lead1_key] = self.__lead1_ecg_block
        samples[PyATC.lead2_key] = self.__lead2_ecg_block
        d = {}
        d[PyATC.file_version_key] = self.__file_version
        d[PyATC.format_block_key] = Utility.to_none_if_none_else_to_dict(self.__format_block)
        d[PyATC.info_block_key] = Utility.to_none_if_none_else_to_dict(self.__info_block)
        d[PyATC.ann_block_key] = Utility.to_none_or_base64_encoded_string(self.__ann_block)
        d[PyATC.samples_key] = samples
        return json.dumps(d)

    def write_json_to_file(self, path):
        with open(path, "w") as f:
            f.write(self.to_json())

    def write_edf_to_file(self, path, local_patient_identification = "X X X X", local_recording_identification = "Y Y Y Y"):
        def get_bytes(bs):
            return b"".join([struct.pack("<B",b) for b in bs])

        def get_right_padded_string_or_whitespace_in_bytes(s, l):
            bs = [32] * l
            if not s is None:
                for i in range(0, len(bs)):
                    if i < len(s):
                        bs[i] = ord(s[i])
            return get_bytes(bs)

        def get_signed_int16_in_bytes(i):
            return struct.pack("<h", i)

        recorded_date = dateutil.parser.parse(self.__info_block.date_recorded)
        num_signals = 0
        signals = []
        signal_information = []
        if not self.__lead1_ecg_block is None:
            signals.append(self.__lead1_ecg_block)
            signal_information.append("ECG Lead_1")
        if not self.__lead2_ecg_block is None:
            signals.append(self.__lead1_ecg_block)
            signal_information.append("ECG Lead_2")

        with open(path, "wb") as f:
            f.write(bytearray([48, 32, 32, 32, 32, 32, 32, 32]))

            f.write(get_right_padded_string_or_whitespace_in_bytes(local_patient_identification, 80))
            f.write(get_right_padded_string_or_whitespace_in_bytes(local_recording_identification, 80))
            f.write(get_right_padded_string_or_whitespace_in_bytes(datetime.datetime.strftime(recorded_date,"%d.%m.%y"), 8))
            f.write(get_right_padded_string_or_whitespace_in_bytes(datetime.datetime.strftime(recorded_date,"%H.%M.%S"), 8))
            f.write(get_right_padded_string_or_whitespace_in_bytes(str(256+256*len(signals)), 8))
            f.write(get_right_padded_string_or_whitespace_in_bytes("", 44))            
            f.write(get_right_padded_string_or_whitespace_in_bytes(str(int(self.get_recording_duration())), 8))
            f.write(get_right_padded_string_or_whitespace_in_bytes("1", 8))
            f.write(get_right_padded_string_or_whitespace_in_bytes(str(len(signals)), 4))
            
            for label in signal_information:
                f.write(get_right_padded_string_or_whitespace_in_bytes(label, 16))
            
            #This is transducer type. We don't know it. So blank
            for _ in signal_information:  
                f.write(get_right_padded_string_or_whitespace_in_bytes("", 80))
            #Physical unit
            for _ in signal_information:
                f.write(get_right_padded_string_or_whitespace_in_bytes("mV", 8))
            #Physical minimum
            for _ in signal_information:
                f.write(get_right_padded_string_or_whitespace_in_bytes("-16.38", 8))
            #Physical maximum
            for _ in signal_information:
                f.write(get_right_padded_string_or_whitespace_in_bytes("16.38", 8))
            #Digital min
            for _ in signal_information:
                f.write(get_right_padded_string_or_whitespace_in_bytes("-32768", 8))
            #Digital min
            for _ in signal_information:
                f.write(get_right_padded_string_or_whitespace_in_bytes("32767", 8))
            #Prefiltering. Don't know
            for _ in signal_information:
                f.write(get_right_padded_string_or_whitespace_in_bytes("prefilter", 80))
            #Number of samples per record. = 1
            for _ in signal_information:
                f.write(get_right_padded_string_or_whitespace_in_bytes(str(self.__format_block.frequency), 8))
            #Reserved space
            for _ in signal_information:
                f.write(get_right_padded_string_or_whitespace_in_bytes("", 32))

            if len(signals) > 0 and len(signals[0]) > 0:
                for i in range(len(signals[0])):
                    for j in range(len(signals)):
                        f.write(get_signed_int16_in_bytes(signals[j][i]))

    def write_to_file(self, path):
        def get_bytes(bs):
            return b"".join([struct.pack("<B",b) for b in bs])
            
        def calculate_checksum(bs):
            s = 0
            #What we get in is different from python 2 vs 3
            if sys.version_info >= (3, 0):
                s = sum(bs)
            else:
                for i in bs:
                    s = s + Utility.byte_to_int(i)
            return s & 0xffffffff
            
        def concat_byte_list_to_string(ls):
            return b"".join(ls)
            
        def get_signed_int16_in_bytes(i):
            return struct.pack("<h", i)

        def get_unsigned_int16_in_bytes(i):
            return struct.pack("<H", i)
            
        def get_unsigned_int32_in_bytes(i):
            return struct.pack("<I", i)
            
        def get_byte_or_null(b):
            return b"\x00" if b is None else b
            
        def get_right_padded_string_or_nulls_in_bytes(s, l):
            bs = [0] * l
            if not s is None:
                for i in range(0, len(bs)):
                    if i < len(s):
                        bs[i] = ord(s[i])
            return get_bytes(bs)

        def get_header_data(fv):
            return get_bytes(PyATC.file_header) + get_bytes(fv)

        def get_info_block(block):
            content = concat_byte_list_to_string([get_right_padded_string_or_nulls_in_bytes("info", 4)
                                                , get_unsigned_int32_in_bytes(264)
                                                , get_right_padded_string_or_nulls_in_bytes(block.date_recorded, 32)
                                                , get_right_padded_string_or_nulls_in_bytes(block.recording_UUID, 40)
                                                , get_right_padded_string_or_nulls_in_bytes(block.phone_UDID, 44)
                                                , get_right_padded_string_or_nulls_in_bytes(block.phone_model, 32)
                                                , get_right_padded_string_or_nulls_in_bytes(block.recorder_software, 32)
                                                , get_right_padded_string_or_nulls_in_bytes(block.recorder_hardware, 32)
                                                , get_right_padded_string_or_nulls_in_bytes(block.location, 52)])
            return concat_byte_list_to_string([content, get_unsigned_int32_in_bytes(calculate_checksum(content))])
            
        def get_format_block(block):
            content = concat_byte_list_to_string([get_right_padded_string_or_nulls_in_bytes("fmt ", 4)
                                                , get_unsigned_int32_in_bytes(8)
                                                , get_byte_or_null(block.fmt_format)
                                                , get_unsigned_int16_in_bytes(block.frequency)
                                                , get_unsigned_int16_in_bytes(block.resolution)
                                                , get_byte_or_null(block.flags)
                                                , get_unsigned_int16_in_bytes(block.reserved)])
            return concat_byte_list_to_string([content, get_unsigned_int32_in_bytes(calculate_checksum(content))])
        
            
        def get_ecg_block(identifier, block):
            ls = []
            for s in block:
                ls.append(get_signed_int16_in_bytes(s))
            content = concat_byte_list_to_string([get_right_padded_string_or_nulls_in_bytes(identifier, 4)
                                                  ,get_unsigned_int32_in_bytes(len(block) * 2)]
                                                  + ls)
            return concat_byte_list_to_string([content, get_unsigned_int32_in_bytes(calculate_checksum(content))])
            
        def get_ann_block(block):
            content = concat_byte_list_to_string([get_right_padded_string_or_nulls_in_bytes("ann ", 4)
                                                , get_unsigned_int32_in_bytes(len(block))
                                                , get_byte_or_null(block)])
            return concat_byte_list_to_string([content, get_unsigned_int32_in_bytes(calculate_checksum(content))])
            
        with open(path, "wb") as f:
            f.write(get_header_data(self.__file_version))
            if not self.__info_block is None:
                f.write(get_info_block(self.__info_block))
            if not self.__format_block is None:
                f.write(get_format_block(self.__format_block))
            if not self.__lead1_ecg_block is None:
                f.write(get_ecg_block("ecg ", self.__lead1_ecg_block))
            #Write second ecg block
            if not self.__lead2_ecg_block is None:
                f.write(get_ecg_block("2ecg", self.__lead2_ecg_block))
            if not self.__ann_block is None:
                f.write(get_ann_block(self.__ann_block))

    @staticmethod
    def read_file(path):
        #We need these
        def character_list_to_string_or_none(t):
            nonZeroIndex = len(t)-1
            while nonZeroIndex >= 0 and t[nonZeroIndex] == 0:
                nonZeroIndex = nonZeroIndex - 1
            filtered = t[0:nonZeroIndex+1]
            if filtered == ():
                return None
            else:
                return ("".join([chr(v) for v in filtered]))
        def read_header(f):
            block_type = f.read(1)
            #EOF
            if block_type == b'':
                return None
            else:
                #Not EOF
                f.seek(-1, 1)
                return (("".join(character_list_to_string_or_none(read_characters(f, 4)))), read_unsigned_int32(f))
        def read_unsigned_int16(f):
            return int(struct.unpack("H", f.read(2))[0])
        def read_signed_int16(f):
            return int(struct.unpack("h", f.read(2))[0])
        def read_unsigned_int32(f):
            return int(struct.unpack("I", f.read(4))[0])
        def read_characters(f, length):
            return struct.unpack("B"*length, f.read(length))

        def validate_checksum_or_raise_exception(f, size):
            #Move back adequately (-8 for block header)
            f.seek(-size-8, 1)

            s = 0
            for i in range(0, size+8):
                s = s + Utility.byte_to_int(f.read(1))
            s = s & 0xffffffff
            checksum = read_unsigned_int32(f)

            #Compare to last uint32 - the checksum
            if not s == checksum:
                raise Exception("Checksum invalid. Expected {0}, was {1}".format(checksum, s))

        #And read the file
        with open(path, "rb") as f:
            signature = read_characters(f, 8)
            file_version = read_characters(f, 4)
            #Is it correct signature?
            assert(signature == PyATC.file_header)
            if not file_version[0] == 3:
                raise UnsupportedFileVersionException(file_version)

            format_block = None
            info_block = None
            lead1_samples = None
            lead2_samples = None
            ann_block = None
            while True:
                maybe_header = read_header(f)
                if maybe_header is None:
                    break
                else:
                    (block_type, block_length) = maybe_header

                    if block_type == "info":
                        date_recorded = character_list_to_string_or_none(read_characters(f, 32))
                        recording_UUID = character_list_to_string_or_none(read_characters(f, 40))
                        phone_UDID = character_list_to_string_or_none(read_characters(f, 44))
                        phone_model = character_list_to_string_or_none(read_characters(f, 32))
                        recorder_software = character_list_to_string_or_none(read_characters(f, 32))
                        recorder_hardware = character_list_to_string_or_none(read_characters(f, 32))
                        location = character_list_to_string_or_none(read_characters(f, 52))

                        validate_checksum_or_raise_exception(f, block_length)

                        info_block = ATCInfoBlock(date_recorded, recording_UUID, phone_UDID, phone_model, recorder_software, recorder_hardware, location)
                    elif block_type == "fmt ":
                        fmt_format = f.read(1)
                        frequency = read_unsigned_int16(f)
                        resolution = read_unsigned_int16(f)
                        flags = f.read(1)
                        reserved = read_unsigned_int16(f)

                        validate_checksum_or_raise_exception(f, block_length)

                        format_block = ATCFormatBlock(fmt_format, frequency, resolution, flags, reserved)
                    elif block_type == "ecg ":
                        lead1_samples = []
                        for i in range (0, int(block_length/2)):
                            lead1_samples.append(read_signed_int16(f))

                        validate_checksum_or_raise_exception(f, block_length)
                    elif block_type == "2ecg":
                        lead2_samples = []
                        for i in range (0, int(block_length/2)):
                            lead2_samples.append(read_signed_int16(f))

                        validate_checksum_or_raise_exception(f, block_length)
                    #Sorry, don't know how this works yet. Likely it contains annotations and flags like "heart rate", "has bradychardia", "has asystole", etc
                    elif block_type == "ann ":
                        ann_block = f.read(block_length)
                        validate_checksum_or_raise_exception(f, block_length)
                    else:
                        raise Exception("Unknown block type: "+block_type)
            return PyATC(file_version, format_block, info_block, lead1_samples, lead2_samples, ann_block)
