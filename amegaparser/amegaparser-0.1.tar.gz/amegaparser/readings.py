"""
Data file binary structure:
    Buffer:
        START = 0
        END = 4

    Time (unsigned):
        DAY_COUNT_START = 4
        DAY_COUNT_END = 8

        SECONDS_SINCE_MIDNIGHT_START = 8
        SECONDS_SINCE_MIDNIGHT_END = 12

    Identification (unsigned):
        PANEL_NUM_START = 12
        PANEL_NUM_END = 16

        ID_START = 16
        ID_END = 20

    Data (float):
        DATA_START = 20
        DATA_END = 24

        DATA_MAX_START = 24
        DATA_MAX_END = 28

        DATA_MIN_START = 28
        DATA_MIN_END = 32
"""

import struct
import csv
import os


class Reading:
    STRUCT_FMT = "<LLLLLfff"

    def __init__(self, data: bytes):
        row = struct.unpack(self.STRUCT_FMT, data)
        self.unknown0 = row[0]
        self.day_count = row[1]
        self.seconds_since_midnight = row[2]
        self.panel_number = row[3]
        self.point_number = row[4]
        self.value = row[5]
        self.high_alarm = row[6]
        self.low_alarm = row[7]

    def to_row(self):
        return [
            self.unknown0,
            self.day_count,
            self.seconds_since_midnight,
            self.panel_number,
            self.point_number,
            self.value,
            self.high_alarm,
            self.low_alarm,
        ]

    def to_bytes(self):
        return self.pack_row(self.to_row())

    @staticmethod
    def pack_row(row):
        return struct.pack(Reading.STRUCT_FMT, *row)

    @staticmethod
    def format_csv_row(row):
        return [
            int(row[0]),
            int(row[1]),
            int(row[2]),
            int(row[3]),
            int(row[4]),
            float(row[5]),
            float(row[6]),
            float(row[7]),
        ]

    @classmethod
    def from_row(cls, row):
        return cls(cls.pack_row(cls.format_csv_row(row)))


headers = [
    "UNKNOWN",
    "day_count",
    "seconds_since_midnight",
    "panel_number",
    "id",
    "value",
    "max",
    "min",
]


def process_bin(f):
    datapoints = []
    while True:
        data = f.read(32)
        if len(data) < 32:
            break
        datapoints.append(Reading(data))
    return datapoints


def bin_to_csv(f, outfile):
    datapoints = process_bin(f)
    dump_datapoints_to_csv(datapoints, outfile)

    print(f"Processed {len(datapoints)} rows.")


def dump_datapoints_to_csv(datapoints, outfile: os.PathLike):
    with open(outfile, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for dp in datapoints:
            writer.writerow(dp.to_row())


def process_csv(f):
    datapoints = []
    reader = csv.reader(f)
    next(reader)  # Skip headers

    for row in reader:
        datapoints.append(Reading.from_row(row))

    return datapoints


def csv_to_bin(f, outfile):
    reader = csv.reader(f)
    next(reader)  # Skip header

    count = 0
    with open(outfile, "wb") as f:
        for row in reader:
            data = Reading.from_row(row)
            f.write(data.to_bytes())
            count += 1

    print(f"Processed {count} rows.")
