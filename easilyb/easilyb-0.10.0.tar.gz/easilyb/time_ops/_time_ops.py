from time import gmtime, time, strptime, strftime, mktime, timezone

import logging
logger = logging.getLogger(__name__)


def epoch_to_iso8601(timestamp):
    try: mlsec = str(timestamp).split('.')[1][:3]
    except: mlsec = "000"
    mlsec = mlsec + "0"*(3-len(mlsec))
    iso_str = strftime("%Y-%m-%dT%H:%M:%S.{}Z".format(mlsec), gmtime(timestamp))
    return iso_str

def iso8601_to_epoch(iso_str):
    str_time, mlsec = iso_str.split('.')
    mlsec = float(mlsec[:-1])/1000
    time_tuple = strptime(str_time+"UTC", "%Y-%m-%dT%H:%M:%S%Z")
    return mktime(time_tuple) - timezone + mlsec

def epoch_to_pathfriendly(timestamp=None):
    if timestamp is None: timestamp = time()
    return strftime("%Y%m%d%H%M%S", gmtime(timestamp))


