from __future__ import absolute_import

import logging
from collections import defaultdict

import gevent.pool

from packy_agent.utils.gevent import async_patched_socket

logger = logging.getLogger(__name__)


def generate_trace_arguments(ping_count, max_hops):
    for ttl in xrange(1, max_hops + 1):
        for probe_number in xrange(ping_count):
            yield {'ttl': ttl, 'probe_number': probe_number}


def trace_once(trace_function_partial, ttl, probe_number):
    try:
        return ttl, probe_number, trace_function_partial(ttl=ttl)
    except Exception:
        logger.exception('Error while trace probing')
        return ttl, probe_number, None


def traceroute_gevent_parallel(trace_function_partial, destination_ip_address,
                               probe_count, max_hops, timeout, max_parallelism=10):
    def trace_function_partial_local(kwargs):
        return trace_once(trace_function_partial, **kwargs)

    destination_hop = max_hops

    results = defaultdict(dict)
    with async_patched_socket():
        pool = gevent.pool.Pool(size=max_parallelism)
        trace_arguments = generate_trace_arguments(probe_count, max_hops)
        for ttl, probe_number, received_probe in pool.imap_unordered(trace_function_partial_local,
                                                                   trace_arguments):
            results[ttl][probe_number] = received_probe
            if received_probe:
                if (received_probe.is_destination_reached or
                        received_probe.hop_ip_address == destination_ip_address):
                    destination_hop = min(ttl, destination_hop)
                    for ttl_local in xrange(destination_hop, 0, -1):
                        if len(results[ttl_local]) < probe_count:
                            break
                    else:
                        pool.kill(timeout=timeout)
                        break

    return [[results[ttl].get(probe_number) for probe_number in xrange(probe_count)]
            for ttl in xrange(1, destination_hop + 1)]
