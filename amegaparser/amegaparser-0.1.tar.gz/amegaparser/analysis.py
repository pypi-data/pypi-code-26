import csv
from . import events
from . import utils
from typing import TYPE_CHECKING, List
from .readings import headers

if TYPE_CHECKING:
    from .readings import Reading


class Alarm:
    def __init__(self, start: events.Event = None, end: events.Event = None):
        self.start_event = start
        self.end_event = end

    def is_in_alarm(self, reading):
        if self.start_event is None and reading < self.end_event:
            return True
        elif self.end_event is None and reading > self.start_event:
            return True


def alarmstatus(reading_data, event_data, outfile):
    alarms = {}  # Point ID to list of Alarms

    for e in event_data:
        if e.activity not in (events.Activity.IN_ALARM, events.Activity.IN_NORMAL_RANGE):
            continue

        if e.identifier not in alarms:
            alarms[e.identifier] = []

        if e.activity == events.Activity.IN_ALARM:
            alarms[e.identifier].append(Alarm(start=e))

        elif e.activity == events.Activity.IN_NORMAL_RANGE:
            try:
                last_alarm = alarms[e.identifier][-1]
            except IndexError:
                alarms[e.identifier].append(Alarm(end=e))
            else:
                last_alarm.end = e

    with open(outfile, mode="w", newline="") as f:
        writer = csv.writer(f)
        for point_number, readings in utils.readings_by_identifier(reading_data).items():
            for r in readings:
                row = r.to_row()
                point_alarms = alarms.get(point_number, [])
                for a in point_alarms:
                    if a.is_in_alarm(r):
                        row.append("IN ALARM")
                writer.writerow(row)

            if len(readings) > 0:
                writer.writerow([])


def bad_value_readings(datapoints: List["Reading"], outfile):
    bad_values = {}
    for dp in datapoints:
        if dp.point_number not in bad_values:
            bad_values[dp.point_number] = []

        if dp.value < dp.low_alarm or dp.value > dp.high_alarm:
            bad_values[dp.point_number].append(dp)

    with open(outfile, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for _, dp_list in sorted(bad_values.items()):
            for dp in dp_list:
                writer.writerow(dp.to_row())
            if len(dp_list) > 0:
                writer.writerow([])
