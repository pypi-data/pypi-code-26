#!/usr/bin/env python3

from enum import Enum, unique
from itertools import chain


@unique
class DataStructure(Enum):
    ATT = 'att'
    CLUSTER = 'cluster'
    CP = 'cp'
    CPIDS = 'cp_ids'
    CPS = 'cps'
    DATA = 'data'
    DATATIMESTAMP = 'data_timestamp'
    EID = 'eid'
    GEOM = 'geom'
    ID = 'id'
    NAME = 'name'
    SECTION = 'section'
    SECTIONIDS = 'section_ids'
    SECTIONS = 'sections'
    SOURCE = 'source'
    VALIDFROM = 'valid_from'
    WEBDATA = 'webdata'
    ZONE = 'zone'
    ZONES = 'zones'


@unique
class Metric(Enum):
    CONFIDENCE = 'Confidence'
    DENSITY = 'Density'
    FLOW = 'Flow'
    FLUIDITY = 'Fluidity'
    OCCUPANCY = 'Occupancy'
    RELATIVESPEED = 'Relative speed'
    SPEED = 'Speed'
    TRAVELTIME = 'Travel time'


@unique
class AttributeEnum(Enum):
    FRC = 'Road category'
    FREEFLOWSPEED = 'Free flow speed'
    MAXSPEED = 'Maximum speed'
    NAME = 'Name'
    SENSORSTATUS = 'Sensor status'
    CPIDS = 'Collection Point Ids'
    TOMTOMIDS = 'TomTom Ids'


# Enum cannot be extended
Attribute = Enum('Attribute', [(e.name, e.value) for e in chain(Metric, AttributeEnum)])


@unique
class Source(Enum):
    CLUSTERS = 'Grenoble clusters'
    METROPME = 'Metro PME'
    SECTIONS = 'Grenoble sections'
    TOMTOMFCD = 'TomTom FCD'
    ZONES = 'Grenoble zones'


@unique
class Channel(Enum):
    CLUSTERS = 1
    METROPME = 2
    SECTIONS = 3
    TOMTOMFCD = 4
    ZONES = 5
