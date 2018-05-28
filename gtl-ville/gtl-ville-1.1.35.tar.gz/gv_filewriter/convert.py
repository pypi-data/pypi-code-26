#!/usr/bin/env python3

import bz2
from concurrent.futures import ThreadPoolExecutor
import os

import gv_protobuf.old_data_pb2 as gv_old_data
import gv_protobuf.data_pb2 as gv_pb_data

METRIC_DICT = {
    1: 'Flow',
    2: 'Speed',
    3: 'Travel time',
    4: 'Confidence',
    5: 'Relative speed',
    6: 'Occupancy'
}
SOURCE_DICT = {
    'PME': 'METROPME',
    'FL': 'METROPME',
    'TOMTOM': 'TOMTOMFCD',
    'CO-RS-SP-TT': 'TOMTOMFCD'
}


def convert_dir(oldfilespath, newbasepath):
    oldfiles = __flatten_paths(oldfilespath, newbasepath)
    cpu = os.cpu_count()
    total = len(oldfiles)
    done = 0
    prev = -1
    with ThreadPoolExecutor(cpu) as executor:
        for _ in executor.map(__flatten_calls, oldfiles):
            done += 1
            prev = __print_per(total, done, prev)


def __print_per(total, done, prev):
    per = int(100 * total / done)
    if per > prev:
        print(per, end='\r')
    return per


def __flatten_paths(oldfilespath, newbasepath):
    oldfiles = []
    for year in os.listdir(oldfilespath):
        yearpath = os.path.join(oldfilespath, year)
        if not os.path.isdir(yearpath):
            continue
        for month in os.listdir(yearpath):
            monthpath = os.path.join(yearpath, month)
            if not os.path.isdir(monthpath):
                continue
            for day in os.listdir(monthpath):
                daypath = os.path.join(monthpath, day)
                if not os.path.isdir(daypath):
                    continue
                for sourcename in os.listdir(daypath):
                    sourcepath = os.path.join(daypath, sourcename)
                    if not os.path.isdir(sourcepath):
                        continue
                    for pbfile in os.listdir(sourcepath):
                        try:
                            time = os.path.splitext(os.path.splitext(pbfile)[0])[0]
                            if '-15' in time or '-45' in time:
                                sourcename = SOURCE_DICT.get(sourcename, sourcename)
                                oldfiles.append((os.path.join(sourcepath, pbfile),
                                                 __get_full_path(newbasepath, sourcename, year, month, day, time),
                                                 sourcename))
                        except:
                            continue
    return oldfiles


def __flatten_calls(oldfile):
    __write_pbf(oldfile[1], __to_pbf(*__parse_old_file(oldfile[0]), oldfile[2]))


def __get_full_path(pbbasepath, sourcename, year, month, day, time):
    fullpath = os.path.join(pbbasepath, sourcename, year, month, day, time + '.pb.gz2')
    directorypath = os.path.dirname(fullpath)
    if not os.path.exists(directorypath):
        os.makedirs(directorypath)
    return fullpath


def __parse_old_file(pbpath):
    olddata = gv_old_data.Data()
    olddata.ParseFromString(__read_bytes(pbpath))
    timestamp = None
    newsamples = dict()
    for oldsample in olddata.sample:
        if timestamp is None:
            timestamp = oldsample.timestamp
        cpeid = oldsample.location_id
        if cpeid not in newsamples:
            newsamples[cpeid] = dict()
        metricid = oldsample.metric_id
        metricname = METRIC_DICT[metricid]
        newsamples[cpeid].update({metricname: oldsample.value})
    return newsamples, timestamp


def __read_bytes(path):
    with open(path, 'rb') as file:
        return bz2.decompress(file.read())


def __to_pbf(newsamples, timestamp, sourcename):
    pbdata = gv_pb_data.CpData()
    for cpeid, data in newsamples.items():
        pbsample = pbdata.sample.add()
        pbsample.cp.eid = cpeid
        pbsample.cp.sourcename = sourcename
        __add_sample_metrics(pbsample, data)
    pbdata.timestamp.FromSeconds(timestamp.ToSeconds())
    return pbdata


def __add_sample_metrics(sample, metrics):
    for metric, value in metrics.items():
        sample.data[metric] = float(value)


def __write_pbf(pbpath, pbdata):
    __write_bytes(pbpath, pbdata.SerializeToString())


def __write_bytes(path, bytesdata):
    with open(path, 'wb') as file:
        file.write(bz2.compress(bytesdata))
