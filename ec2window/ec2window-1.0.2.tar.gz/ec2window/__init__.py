"""Provides the run_ec2_instance context manager."""

import contextlib
import logging

LOG = logging.getLogger(__name__)


def get_instance_state(instance):
    """Get the current state of |instance|."""
    return instance.state['Name']


def ensure_instance_started(instance):
    """Start |instance| and wait until it is started."""
    state = get_instance_state(instance)
    LOG.debug('current state of %s: %s', instance.id, state)

    # Wait for stopping to become stopped
    if state == 'stopping':
        LOG.info('waiting for %s to stop', instance.id)
        instance.wait_until_stopped()
        state = get_instance_state(instance)

    # Start the instance if necessary
    if state != 'running':
        instance.start()
        LOG.info('waiting for %s to start', instance.id)
        instance.wait_until_running()


def ensure_instance_stopped(instance):
    """Stop |instance| and wait until it is stopped."""
    instance.stop()
    LOG.info('waiting for %s to stop', instance.id)
    instance.wait_until_stopped()


@contextlib.contextmanager
def run_ec2_instance(instance):
    """Context manager that starts |instance| and stops it on exit."""
    try:
        ensure_instance_started(instance)
        yield
    finally:
        ensure_instance_stopped(instance)
