# -*- coding: utf-8 -*-
"""Get a Cluster Logger object."""

from .logger import ClusterLogger


__version__ = '0.4.0'


def initLogger(project: str,
               application: str,
               fluent_host='fluentd',
               fluent_port=24224,
               path='',
               env_keys=[],
               properties={},):
    """Create the config for log messages."""
    ClusterLogger.fromConfig(project,
                             application,
                             fluent_host,
                             fluent_port,
                             path,
                             env_keys,
                             properties,)


def getLogger(name: str,) -> ClusterLogger:
    """Get a logger."""
    return ClusterLogger(name,)
