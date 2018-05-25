""" Subscribers
"""
import os
import logging
from plone.app.async.subscribers import set_quota
logger = logging.getLogger('eea.epub')


def getMaximumThreads(queue):
    """ Get the maximum threads per queue
    """
    size = 0
    for da in queue.dispatchers.values():
        if not da.activated:
            continue
        for _agent in da.values():
            size += 3
    return size or 1

def configureQueue(event):
    """ Configure zc.async queue for ePub export jobs
    """
    queue = event.object

    try:
        size = int(os.environ.get('EEAEPUB_ASYNC_THREADS',
                                  getMaximumThreads(queue)))
    except Exception, err:
        logger.exception(err)
        size = 1

    set_quota(queue, 'epub', size=size)
    logger.info(
        "quota 'epub' with size %r configured in queue %r.", size, queue.name)
