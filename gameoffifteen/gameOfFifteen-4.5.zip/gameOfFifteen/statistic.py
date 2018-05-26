#!/usr/bin/python3
# -*- coding: UTF-8 -*-


"""Modul contains implementation for statistic."""


__license__ = "Copyright 2018 by Vikarowitsch"
__author__ = "Vikarowitsch"


import os.path
import datetime
import json


class Statistic:

    """ Implementation statistc."""

    __scriptPath = os.path.dirname(__file__)
    __relativeRepositoryName = "{0}/Repository/statistic.txt".format(__scriptPath)
    __datetimeformat = '%Y-%m-%d %H:%M:%S %Z'
    __gamedurationformat = '%H:%M:%S %Z'

    def __init__(self):
        """Intialize object."""
        if os.path.isfile(Statistic.__relativeRepositoryName) is False:
            Statistic.create_new_statistic()

    def add(self, solution, count_of_moves, count_of_buttons, game_time_in_seconds):
        """Add information to statistic."""
        data = Statistic.get_statistic()
        now = datetime.datetime.now().strftime(Statistic.__datetimeformat)
        with open(Statistic.__relativeRepositoryName, mode='w', encoding='utf-8') as file:
            entry = str("{0} {1} Züge={2} Knöpfe={3} Spieldauer {4}".format(now,
                        solution, count_of_moves, count_of_buttons,
                        Statistic.format_duration(game_time_in_seconds)))
            data.append(entry)
            json.dump(data, file)

    def get_statistic():
        """Read an return statistic file."""
        with open(Statistic.__relativeRepositoryName, mode='r', encoding='utf-8') as file:
            try:
                data = json.load(file)
            except:
                data = Statistic.create_new_statistic()
            return data

    def create_new_statistic():
        """Create new statistic file content and return it as string."""
        with open(Statistic.__relativeRepositoryName, mode='w', encoding='utf-8') as file:
            now = datetime.datetime.now()
            data = []
            data.append(str("{0} Initialisiere Statistik".format(now.strftime(Statistic.__datetimeformat))))
            json.dump(data, file)
        return Statistic.get_statistic()

    def format_duration(duration_in_secs):
        """Convert duration in seconds to user friedly format. Return as string."""
        return str(datetime.timedelta(seconds=int(duration_in_secs)))
