import struct
import csv
from enum import Enum, unique
from . import utils

headers = [
    "UNKNOWN",
    "day_count",
    "seconds_since_midnight",
    "identifier",
    "UNKNOWN",
    "UNKNOWN",
    "UNKNOWN",
    "UNKNOWN",
    "activity",
    "qualifier",
    "UNKNOWN",
]


@unique
class Activity(Enum):
    IN_NORMAL_RANGE = 0
    PENDING_ALARM = 1
    IN_ALARM = 2
    DIALING = 3
    ACK_FROM_PHONE = 4
    LIST_COMPLETED = 5
    ENABLED = 6
    INPUT_INHIBITED = 7
    SHORTED_PROBE = 8
    OPEN_PROBE = 9
    PROGRAM_CHANGE = 10
    INPUT_CALIBRATED = 11
    GATEWAY = 13
    IO_PANEL = 14
    DIALER = 15
    SERVER = 16
    TERMINAL = 17
    USER_ACTIVITIES = 18
    REPORT_REVIEWED = 19


@unique
class Qualifier(Enum):
    ONLINE = 0
    OFFLINE = 1
    BATTERY = 2
    ONLINE_COMM_B = 3
    PHONE_LINE_FAILURE = 4
    PROGRAM_CHANGE = 5
    INPUT = 6
    ALL_INPUTS = 7
    GROUP = 8
    LOG_MEMORY_CRITICAL = 9
    READINGS_OVERWRITE = 10
    EVENT_MEMORY_OVERWRITE = 11
    INVALID_PASSCODE = 12
    TIME_OR_DATE_CHANGE = 13
    BATTERY_CHARGE_OK = 14
    WIRELESS_PROBE_ID = 15
    MANUAL_ADDED_ACTIVITY = 16


class Event:
    STRUCT_FMT = "<LLLLffffLLL"

    def __init__(self, data: bytes):
        row = struct.unpack(self.STRUCT_FMT, data)
        self.unknown0 = row[0]
        self.day_count = row[1]
        self.seconds_since_midnight = row[2]
        self.identifier = row[3]
        self.unknown1 = row[4]
        self.unknown2 = row[5]
        self.unknown3 = row[6]
        self.unknown4 = row[7]
        self.activity = Activity(row[8])
        self.qualifier = Qualifier(row[9])
        self.unknown5 = row[10]

    def __lt__(self, other):
        return (
            self.day_count < other.day_count
            or self.seconds_since_midnight < other.seconds_since_midnight
            or self.identifier < other.identifier
        )

    def to_bytes(self):
        return struct.pack(self.STRUCT_FMT, *self.to_row())

    def to_row(self):
        return [
            self.unknown0,
            self.day_count,
            self.seconds_since_midnight,
            self.identifier,
            self.unknown1,
            self.unknown2,
            self.unknown3,
            self.unknown4,
            self.activity.value,
            self.qualifier.value,
            self.unknown5,
        ]

    @staticmethod
    def is_amega_point(identifier):
        return True


def process_bin(f):
    ret = []
    while True:
        data = f.read(44)
        if len(data) < 44:
            break
        ret.append(Event(data))
    return ret


def bin_to_csv(f, outfile):
    data = process_bin(f)

    with open(outfile, mode="w", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row)


def process_csv(f):
    ret = []
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        ret.append(utils.format_row(Event.STRUCT_FMT, row))
    return ret


def csv_to_bin(f, outfile):
    data = process_csv(f)

    with open(outfile, mode="wb") as out:
        for row in data:
            out.write(struct.pack(Event.STRUCT_FMT, *row))
